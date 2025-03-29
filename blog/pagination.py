from rest_framework.pagination import PageNumberPagination

class BlogPageNumberPagination(PageNumberPagination):
    page_size = 6  # 每页显示6条
    page_size_query_param = 'page_size'  # 允许客户端通过此参数自定义每页数量
    max_page_size = 20  # 最大每页数量限制 