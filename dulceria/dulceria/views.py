from django.shortcuts import render


def custom_404(request, exception):
    """
    Vista personalizada para errores 404.
    """
    return render(request, "404.html", status=404)

