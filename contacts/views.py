from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ContactForm
from .models import Contact


@require_GET
def contact_list(request):
    return render(request, "contacts/index.html", {
        "name": "Naila Husna",
        "contacts": Contact.objects.order_by("pk"),
        "form": ContactForm(),
    })


@require_POST
def contact_add(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(request, "contacts/_feedback.html", {"form": form}, status=422)

    contact = form.save()
    query = request.POST.get("q", "").strip()
    visible = Contact.objects.filter(pk=contact.pk, name__icontains=query).exists()
    return render(request, "contacts/_contact_added.html", {
        "contact": contact,
        "visible": visible,
        "feedback": "Kontak berhasil ditambahkan!",
    }, status=201)


@require_GET
def contact_search(request):
    query = request.GET.get("q", "").strip()
    contacts = Contact.objects.filter(name__icontains=query).order_by("pk")
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


@require_GET
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    form = ContactForm(instance=contact, auto_id=f"edit-{pk}-%s")
    return render(request, "contacts/_contact_edit_row.html", {
        "contact": contact,
        "form": form,
    })


@require_GET
def contact_row(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_row.html", {"contact": contact})


@require_http_methods(["PUT"])
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    data = QueryDict(request.body)
    form = ContactForm(data, instance=contact, auto_id=f"edit-{pk}-%s")
    if not form.is_valid():
        return render(request, "contacts/_contact_edit_row.html", {
            "contact": contact,
            "form": form,
        }, status=422)

    contact = form.save()
    query = data.get("q", "").strip()
    if not Contact.objects.filter(pk=contact.pk, name__icontains=query).exists():
        return HttpResponse("")
    return render(request, "contacts/_contact_row.html", {"contact": contact})


@require_http_methods(["DELETE"])
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return HttpResponse("")
