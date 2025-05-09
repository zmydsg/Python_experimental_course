class BOOK ():
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn

class EBOOK(BOOK):
    def __init__(self, title, author, isbn,format):
        self.format = format
        super().__init__(title,author,isbn)

class PrintedBOOK(EBOOK):
    def __init__(self,title,author,isbn,format,pagecount):
        super().__init__(title, author, isbn,format)
        self.pagecount = pagecount

book = BOOK("Python", "ZPY", "123456")
print(book.title, book.author, book.isbn)

ebook = EBOOK("JAVASCRIPT", "CHUNGSUBIN", "1998","pdf")
print(ebook.title,ebook.author, ebook.author,ebook.isbn,ebook.format)

printedbook = PrintedBOOK("Python", "ZPY", "123456","docx","100")
print(printedbook.title,printedbook.author,printedbook.isbn,printedbook.format,printedbook.pagecount)





    