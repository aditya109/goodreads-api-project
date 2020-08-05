class Book:
    def __init__(self, book_name, authors, ID, isbn, isbn13, publication_date, best_book_id, reviews_count,
                 ratings_sum, ratings_count, text_reviews_count, average_rating):
        self.book_name = book_name
        self.authors = authors
        self.id = ID
        self.isbn = isbn
        self.isbn13 = isbn13
        self.publication_date = publication_date
        self.best_book_id = best_book_id
        self.reviews_count = reviews_count
        self.ratings_sum = ratings_sum
        self.ratings_count = ratings_count
        self.text_reviews_count = text_reviews_count
        self.average_ratings = average_rating

    def get_book_name(self):
        return self.book_name

    def set_book_name(self, value):
        self.book_name = value

    def get_authors(self):
        return self.authors

    def set_authors(self, value):
        self.authors = value

    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_isbn(self):
        return self.isbn

    def set_isbn(self, value):
        self.isbn = value

    def get_isbn13(self):
        return self.isbn13

    def set_isbn13(self, value):
        self.isbn13 = value

    def get_publication_date(self):
        return self.publication_date

    def set_publication_date(self, value):
        self.publication_date = value

    def get_best_book_id(self):
        return self.best_book_id

    def set_best_book_id(self, value):
        self.best_book_id = value

    def get_reviews_count(self):
        return self.reviews_count

    def set_reviews_count(self, value):
        self.reviews_count = value

    def get_ratings_sum(self):
        return self.ratings_sum

    def set_ratings_sum(self, value):
        self.ratings_sum = value

    def get_ratings_count(self):
        return self.ratings_count

    def set_ratings_count(self, value):
        self.ratings_count = value

    def get_text_reviews_count(self):
        return self.text_reviews_count

    def set_text_reviews_count(self, value):
        self.text_reviews_count = value

    def get_average_ratings(self):
        return self.average_ratings

    def set_average_ratings(self, value):
        self.average_ratings = value

    def Wingardium_Leviosa(self):
        return f"Book Name : {self.book_name}\n" \
               f"Authors : {self.authors}\n" \
               f"ID(Goodreads) : {self.id}\n" \
               f"ISBN : {self.isbn}\n" \
               f"ISBN13 : {self.isbn13}\n" \
               f"Publication Date : {self.publication_date}\n" \
               f"Best Book ID : {self.best_book_id}\n" \
               f"Reviews Count : {self.reviews_count}\n" \
               f"Ratings Sum : {self.ratings_sum}\n" \
               f"Ratings Count : {self.ratings_count}\n" \
               f"Text Reviews Count : {self.text_reviews_count}\n" \
               f"Average Ratings : {self.average_ratings}"


class BookBuilder:
    def __init__(self):
        self.book_name = ""
        self.authors = []
        self.id = ""
        self.isbn = ""
        self.isbn13 = ""
        self.publication_date = ""
        self.best_book_id = ""
        self.reviews_count = ""
        self.ratings_sum = ""
        self.ratings_count = ""
        self.text_reviews_count = ""
        self.average_ratings = ""

    @staticmethod
    def initialize():
        return BookBuilder()

    def withBookName(self, book_name):
        self.book_name = book_name
        return self

    def hasAuthors(self, authors):
        self.authors = authors
        return self

    def hasId(self, id):
        self.id = id
        return self

    def hasISBN(self, isbn):
        self.isbn = isbn
        return self

    def hasISBN13(self, isbn13):
        self.isbn13 = isbn13
        return self

    def wasPublishedOn(self, publication_date):
        self.publication_date = publication_date
        return self

    def hasBestBookId(self, best_book_id):
        self.best_book_id = best_book_id
        return self

    def hasReviewsCount(self, reviews_count):
        self.reviews_count = reviews_count
        return self

    def hasRatingsSum(self, ratings_sum):
        self.ratings_sum = ratings_sum
        return self

    def hasRatingsCount(self, ratings_count):
        self.ratings_count = ratings_count
        return self

    def hasTextReviewsCount(self, text_reviews_count):
        self.text_reviews_count = text_reviews_count
        return self

    def hasAverageRatings(self, average_ratings):
        self.average_ratings = average_ratings
        return self

    def build(self):
        return Book(self.book_name, self.authors, self.id, self.isbn, self.isbn13, self.publication_date,
                    self.best_book_id, self.reviews_count, self.ratings_sum, self.ratings_count,
                    self.text_reviews_count, self.average_ratings)

#
# obj = BookBuilder.initialize().withBookName("The Girl with the Dragon Tattoo").hasAuthors(["Stieg Larsson", "Reg Keeland"]).hasId("2429135").wasPublishedOn("16-9-2008").hasBestBookId("2429135").hasReviewsCount("3677258").hasRatingsSum(
#         "10596196").hasRatingsCount("2561726").hasTextReviewsCount("68261").hasAverageRatings("4.14").build()
#
# print(obj)