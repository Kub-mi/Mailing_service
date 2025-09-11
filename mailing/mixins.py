from django.core.exceptions import PermissionDenied


class OwnerOrManagerRequiredMixin:
    """
    Доступ к объекту: владелец или пользователь с правом глобального просмотра (менеджер).
    Для редактирования/удаления — менеджеру запрещаем менять чужие объекты (только просмотр).
    """

    manager_perm = None  # например: "mailing.view_all_clients"

    def has_manager_perm(self):
        return bool(self.manager_perm and self.request.user.has_perm(self.manager_perm))

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # На чтение: владелец ИЛИ менеджер
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            if obj.owner_id == self.request.user.id or self.has_manager_perm():
                return obj
            raise PermissionDenied("Нет доступа")
        # На изменение/удаление: ТОЛЬКО владелец
        if obj.owner_id != self.request.user.id:
            raise PermissionDenied("Менеджер не может изменять/удалять чужие объекты")
        return obj


class OwnerFilteredQuerysetMixin:
    """
    В list/detail: пользователю показываем только своё, менеджеру — всё.
    """

    manager_perm = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if self.manager_perm and user.has_perm(self.manager_perm):
            return qs
        return qs.filter(owner=user)
