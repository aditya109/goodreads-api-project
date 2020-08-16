class Review:
    """
    Review class for storing `Review` information
    """
    def __init__(self, ID, reviewer_id, rating, likes, review, book_id):
        self.review_id = ID
        self.reviewer_id = reviewer_id
        self.rating = rating
        self.likes = likes
        self.review = review
        self.book_id = book_id

    def get_review_id(self):
        return self.review_id

    def set_review_id(self, value):
        self.review_id = value

    def get_reviewer_id(self):
        return self.reviewer_id

    def set_reviewer_id(self, value):
        self.reviewer_id = value

    def get_rating(self):
        return self.rating

    def set_rating(self, value):
        self.rating = value

    def get_likes(self):
        return self.likes

    def set_likes(self, value):
        self.likes = value

    def get_review(self):
        return self.review

    def set_review(self, value):
        self.review = value

    def get_book_id(self):
        return self.book_id

    def set_book_id(self, value):
        self.book_id = value

    def Wingardium_Leviosa(self):
        print(f"==========================================================\n"
              f"Review ID : {self.review_id}\n"
              f"Reviewer ID : {self.reviewer_id}\n"
              f"Rating : {self.rating}\n"
              f"Likes : {self.likes}\n"
              f"Review : {self.review}\n"
              f"Book ID : {self.book_id}")


class ReviewBuilder:
    """
    ReviewBuilder class for piecewise contruction of `Review` object
    """
    def __init__(self):
        self.review_id = ""
        self.reviewer_id = ""
        self.rating = ""
        self.likes = ""
        self.review = ""
        self.book_id = ""

    @staticmethod
    def initialize():
        return ReviewBuilder()

    def hasReviewID(self, review_id):
        self.review_id = review_id
        return self

    def byReviewerID(self, reviewer_id):
        self.reviewer_id = reviewer_id
        return self

    def hasRating(self, rating):
        self.rating = rating
        return self

    def hasLikes(self, likes):
        self.likes = likes
        return self

    def hasText(self, review):
        self.review = review
        return self

    def hasBookId(self, book_id):
        self.book_id = book_id
        return self

    def build(self):
        return Review(self.review_id, self.reviewer_id, self.rating, self.likes, self.review, self.book_id)
