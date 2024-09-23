import asyncio
import logging

import asyncpg
import grpc
import grpc.experimental.aio

import book_service_pb2_grpc as book_service_pb2_grpc
from book_service_pb2 import BookListResponse, BookResponse
from config import settings


class AsyncBookService(book_service_pb2_grpc.BooksServicer):

    async def GetBook(self, request, context):
        conn = await asyncpg.connect(**settings.CONNECTION_DATA)
        book_from = await conn.fetch(f"""SELECT id, name, author,
                                     to_char(uploaded_at, 'dd-mm-yyyy')
                                        AS uploaded_at
                                     FROM book where book.id={request.id};
                                     """)
        dict_row = dict(book_from[0])
        await conn.close()
        book = BookResponse(**dict_row)
        return book


    async def GetBooks(self, request, context):
        conn = await asyncpg.connect(**settings.CONNECTION_DATA)
        response = await conn.fetch("""SELECT id, name, author,
                                    to_char(uploaded_at, 'dd-mm-yyyy')
                                        AS uploaded_at
                                    FROM book;""")
        book_list = []
        for row in response:
            book_list.append(BookResponse(**row))
        await conn.close()
        return BookListResponse(book=book_list)


async def main():
    grpc.experimental.aio.init_grpc_aio()
    server = grpc.experimental.aio.server()
    server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")
    book_service_pb2_grpc.add_BooksServicer_to_server(
        AsyncBookService(), server
    )
    await server.start()
    logging.info('Сервер запущен.')
    await server.wait_for_termination()


def start_server():
    asyncio.run(main())


if __name__ == '__main__':
    start_server()
