import os, tempfile

from django.http import HttpResponse, HttpResponse ,HttpResponseRedirect, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.template.loader import get_template
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from PyPDF2 import PdfReader, PdfWriter, Transformation, PageObject
from PyPDF2.generic import RectangleObject
from PyPDF2 import PaperSize

from .models import (
    Invoice
)
from .forms import (
    BillOfLadingToTripForm,
    BillOfLadingToInvoiceForm,
    BillOfLadingForm,
)

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration



def index(request):
    args = {
        'invoices' : Invoice.objects.all().order_by('date')
    }

    return render(request, 'invoices_index.html', args)


def pdf(request, invoice):
    args = {
        "invoice" : invoice,
        "leading_zeros_invoice_number" : invoice.get_leading_zeros_invoice_number(),
    }

    # Get the template
    template = get_template('invoice_as_pdf.html')
    
    # Render the template
    rendered_html = template.render(args)

    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False) as generated_invoice_pdf, tempfile.NamedTemporaryFile(delete=False) as complete_invoice_pdf, tempfile.NamedTemporaryFile(delete=False) as modified_attachment:
        # Generate the PDF using WeasyPrint
        font_config = FontConfiguration()
        invoice_css = CSS(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/css/invoice.css'), font_config=font_config)
        bootstrap_css = CSS(url='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css')
        HTML(string=rendered_html, base_url=request.build_absolute_uri()).write_pdf(target=generated_invoice_pdf, stylesheets=[bootstrap_css,invoice_css],font_config=font_config)

        # Adjust attachment
        invoice_attachment = invoice.trip.attachment.file.open('r')
        pdf_reader = PdfReader(invoice_attachment)
        pdf_writer = PdfWriter()

        A4_w = PaperSize.A4.width
        A4_h = PaperSize.A4.height

        # Iterate through each page of the existing PDF
        for page in pdf_reader.pages:
            # resize page to fit *inside* A4
            h = float(page.mediabox.height)
            w = float(page.mediabox.width)
            scale_factor = min(A4_h/h, A4_w/w)

            transform = Transformation().scale(scale_factor,scale_factor).translate(0, 0)
            page.add_transformation(transform)

            page.cropbox = RectangleObject((0, 0, A4_w, A4_h))

            # merge the pages to fit inside A4

            # prepare A4 blank page
            page_A4 = PageObject.create_blank_page(width = A4_w, height = A4_h)
            page.mediabox = page_A4.mediabox
            page_A4.merge_page(page)

            # Add the modified page to the new PDF
            pdf_writer.add_page(page)
        pdf_writer.write(modified_attachment)
        pdf_writer.close()

        # Combine PDF with attachment
        merger = PdfWriter()
        for pdf in [generated_invoice_pdf, modified_attachment]:
            merger.append(pdf)
        merger.write(complete_invoice_pdf)
        merger.close()


    # Read the PDF file
    with open(complete_invoice_pdf.name, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="' + invoice.get_pdf_name() + '.pdf"'
        return response
    
# @login_required
def generate(request):
    if request.method == 'POST':
        trip_form = BillOfLadingToTripForm(request.POST, request.FILES)
        invoice_form = BillOfLadingToInvoiceForm(request.POST , request.FILES)
        bill_of_lading_form = BillOfLadingForm(request.POST, request.FILES)

        # check whether it's valid:
        if trip_form.is_valid() and invoice_form.is_valid() and bill_of_lading_form.is_valid() and request.user.is_authenticated:
            invoice_number = bill_of_lading_form.cleaned_data["optional_invoice_number"]
            # Check if invoice number is given, if not then set it as new max
            if invoice_number is None:
                max = Invoice.objects.aggregate(Max('invoice_number')).get('invoice_number__max')
                invoice_number = max + 1
            elif Invoice.objects.get(invoice_number=invoice_number) is not None: 
                raise Http404("An invoice with that number already exists.")

                
            bill_of_lading = bill_of_lading_form.cleaned_data["bill_of_lading"]
            trailer = trip_form.cleaned_data["trailer"]
            ship_to_address = trip_form.cleaned_data["ship_to_address"]
            rate = invoice_form.cleaned_data["rate"]
            notes = invoice_form.cleaned_data["notes"]

            trip = BillOfLadingToInvoiceForm.generate_trip(
                invoice_number,
                trailer, 
                ship_to_address
            )

            invoice = BillOfLadingToInvoiceForm.generate_invoice(
                invoice_number,
                bill_of_lading,
                trip,
                rate,
                notes
            )

            if 'generate_and_save' in request.POST:
                trip.save()
                invoice.save()

                reverse_view_url = reverse('view_invoice_as_pdf', kwargs={'invoice_number': invoice.invoice_number})
                return HttpResponseRedirect(reverse_view_url)
            elif 'generate' in request.POST:
                ...

            return pdf(request, invoice)
    else:
        trip_form = BillOfLadingToTripForm()
        invoice_form = BillOfLadingToInvoiceForm()
        bill_of_lading_form = BillOfLadingForm()

    args = {
        "trip_form" : trip_form,
        "invoice_form" : invoice_form,
        "bill_of_lading_form" : bill_of_lading_form,
    }

    return render(request, 'invoice_generate.html', args)


def view_invoice_as_pdf(request, invoice_number):
    try:
        invoice = Invoice.objects.get(invoice_number=invoice_number)

        if not request.user.is_authenticated:
            raise PermissionDenied
            
    except Invoice.DoesNotExist:
        raise Http404("Invoice does not exist.")
    except Invoice.MultipleObjectsReturned:
        raise Http404("More than one invoice with the same number exists.")
    
    return pdf(request, invoice)
