from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escapejs

from .models import (MediaHost, Audio, Video)
from .forms import VideoAdminForm, AudioAdminForm

from opps.core.admin import apply_opps_rules
from opps.containers.admin import ContainerAdmin


@apply_opps_rules('multimedias')
class MediaAdmin(ContainerAdmin):
    add_form_template = u'admin/change_form.html'
    change_form_template = u'multimedias/admin/change_form.html'

    readonly_fields = ContainerAdmin.readonly_fields[:]
    readonly_fields += ['published', 'date_available']

    change_readonly_fields = ContainerAdmin.readonly_fields[:]
    change_readonly_fields += ['published', 'date_available', 'media_file']

    actions = ContainerAdmin.actions[:]
    actions += ['resend_uolmais', ]

    search_fields = ['title', 'headline', 'slug', 'channel_name', 'tags']
    # search_fields = ['title', 'slug', 'channel_name']

    raw_id_fields = ContainerAdmin.raw_id_fields[:]
    raw_id_fields += ['related_posts']

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug', 'get_http_absolute_url',
                       'short_url', ('main_image', 'image_thumb'))}),
        (_(u'Content'), {
            'fields': ('short_title', 'hat',
                       'headline', 'json', 'media_file', 'tags',
                       'related_posts')}),
        (_(u'Relationships'), {
            'fields': ('channel', 'mirror_channel',)}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available',
                       'show_on_root_channel')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.change_readonly_fields
        return self.readonly_fields

    def resend_uolmais(self, request, queryset):
        for media in queryset.select_related('uolmais'):
            media.uolmais.host_id = None
            media.uolmais.url = None
            media.uolmais.retries = 0
            media.uolmais.embed = ''
            media.uolmais.status = MediaHost.STATUS_NOT_UPLOADED
            media.uolmais.status_message = ''
            media.uolmais.save()

            media.published = False
            media.save()
    resend_uolmais.short_description = _(u"Resend UOLMais media")

    def get_list_display(self, request):
        list_display = self.list_display
        pop = request.GET.get('pop')
        if pop == 'oppseditor':
            list_display = ['opps_editor_select'] + list(list_display)
        return list_display

    def opps_editor_select(self, obj):
        source = obj.get_media_embed()
        source = escapejs(source)
        return u'''
        <a href="#"
        onclick="window.parent.tinymce.activeEditor.selection
        .setContent('{0}');
        window.parent.tinymce.activeEditor.windowManager
        .close(window);">{1}</a>
        '''.format(source, _(u'Select'))
    opps_editor_select.short_description = _(u'Select')
    opps_editor_select.allow_tags = True


@apply_opps_rules('multimedias')
class VideoAdmin(MediaAdmin):
    form = VideoAdminForm
    actions = MediaAdmin.actions[:]
    actions += ['resend_youtube', ]

    def resend_youtube(self, request, queryset):
        for media in queryset.select_related('youtube'):
            media.youtube.host_id = None
            media.youtube.url = None
            media.youtube.retries = 0
            media.youtube.embed = ''
            media.youtube.status = MediaHost.STATUS_NOT_UPLOADED
            media.youtube.status_message = ''
            media.youtube.save()
    resend_youtube.short_description = _(u"Resend Youtube video")


@apply_opps_rules('multimedias')
class AudioAdmin(MediaAdmin):
    form = AudioAdminForm


admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
