import views.common.common_views as common_views

urls = [
    (r'upload/?', common_views.UploadHandler),
    (r'feedback/?', common_views.FeedbackHandler),
]