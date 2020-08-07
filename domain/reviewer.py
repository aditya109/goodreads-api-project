class Reviewer:
    def __init__(self, reviewer_name, reviewer_id, shelves, number_of_reviews, friends_count, following, followers):
        self.reviewer_name = reviewer_name
        self.reviewer_id = reviewer_id
        self.shelves = shelves
        self.number_of_reviews = number_of_reviews
        self.friends_count = friends_count
        self.following = following  # list of reviewer ids
        self.followers = followers  # list of reviewer ids

    def get_reviewer_name(self):
        return self.reviewer_name

    def get_reviewer_id(self):
        return self.reviewer_id

    def get_shelves(self):
        return self.shelves

    def get_number_of_reviews(self):
        return self.number_of_reviews

    def get_friends_count(self):
        return self.friends_count

    def get_following(self):
        return self.following

    def get_followers(self):
        return self.followers

    def Wingardium_Leviosa(self):
        print(f"Reviewer Name : {self.reviewer_name}\n"
              f"Reviewer ID : {self.reviewer_id}\n"
              f"Number Of Reviews : {self.number_of_reviews}\n"
              f"Friends Count : {self.friends_count}\n"
              f"Following : {self.following}\n"
              f"Followers : {self.followers}\n"
              f"Shelves : {len(self.shelves)}\n"
              )
        for shelf in self.shelves:
            print(shelf)


class Shelf:
    def __init__(self, shelf_id, shelf_name, book_count):
        self.shelf_id = shelf_id
        self.shelf_name = shelf_name
        self.book_count = book_count


    def get_shelf_id(self):
        return self.shelf_id

    def get_shelf_name(self):
        return self.shelf_name

    def get_book_count(self):
        return self.book_count

    def __str__(self):
        return f"=====================================\n" \
               f"Shelf Name : {self.shelf_name}  " \
               f"Shelf ID : {self.shelf_id} " \
               f"Book Count : {self.book_count}"


class ShelfBuilder:
    def __init__(self):
        self.shelf_id = ""
        self.shelf_name = ""
        self.book_count = ""

    @staticmethod
    def initialize():
        return ShelfBuilder()

    def hasShelfID(self, shelf_id):
        self.shelf_id = shelf_id
        return self

    def hasShelfName(self, self_name):
        self.shelf_name = self_name
        return self

    def hasBookCount(self, book_count):
        self.book_count = book_count
        return self

    def build(self):
        return Shelf(self.shelf_id, self.shelf_name, self.book_count)


class ReviewerBuilder:
    def __init__(self):
        self.reviewer_name = ""
        self.reviewer_id = ""
        self.shelves = []
        self.number_of_reviews = ""
        self.friends_count = ""
        self.following = []  # list of reviewer ids
        self.followers = []  # list of reviewer ids

    @staticmethod
    def initialize():
        return ReviewerBuilder()

    def hasName(self, name):
        self.reviewer_name = name
        return self

    def hasID(self, ID):
        self.reviewer_id = ID
        return self

    def hasShelves(self, shelves):
        self.shelves = shelves
        return self

    def hasTotalReviews(self, number_of_reviews):
        self.number_of_reviews = number_of_reviews
        return self

    def hasFriendsCount(self, friends_count):
        self.friends_count = friends_count
        return self

    def hasFollowing(self, following):
        self.following = following
        return self

    def hasFollowers(self, followers):
        self.followers = followers
        return self

    def build(self):
        return Reviewer(self.reviewer_name,
                        self.reviewer_id,
                        self.shelves,
                        self.number_of_reviews,
                        self.friends_count,
                        self.following,
                        self.followers)
