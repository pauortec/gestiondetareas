def rol_usuario(request):
    if request.user.is_authenticated:
        return {'es_admin': request.user.groups.filter(name='Administrador').exists()}
    return {'es_admin': False}
