from concurrent import futures

import grpc

import grpc_service.book_service_pb2_grpc as book_service_pb2_grpc
from grpc_service.book_service_pb2 import (BookListRequest, BookListResponse,
                                           BookRequest, BookResponse)


class BookService(
    book_service_pb2_grpc.BooksServicer
):

    def GetBook(self, request, context):
        # if request.category not in books_by_category:
        #     context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")

        book = BookResponse(id=request.id, name='War & Peace', author='Tolstoy', uploaded_at='date today')
        return book

    def GetBooks(self, request, context):
        books = [
            BookResponse(id=1, name='War & Peace', author='Tolstoy', uploaded_at='date today'),
            BookResponse(id=2, name='Anna Karenina', author='Tolstoy', uploaded_at='date today')
        ]
        return BookListResponse(book=books)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_service_pb2_grpc.add_BooksServicer_to_server(
        BookService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
