from django.contrib import admin
from .models import Comment, WordDict, CommentReply

# Register your models here.
class CommentAdmin(admin.ModelAdmin):
    pass
class WordDictAdmin(admin.ModelAdmin):
    pass
class CommentReplyAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comment, CommentAdmin)
admin.site.register(WordDict, WordDictAdmin)
admin.site.register(CommentReply, CommentReplyAdmin)
