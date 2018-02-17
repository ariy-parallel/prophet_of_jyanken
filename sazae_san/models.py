from django.db import models

class Episode(models.Model):
    HANDS = [("グー", "グー"), ("チョキ", "チョキ"), ("パー", "パー")]
    air_time = models.DateField()
    hand = models.CharField(max_length = 3, choices = HANDS)

    def hand_is_rock(self):
        return self.__to_int(self.hand == self.HANDS[0][0])

    def hand_is_sessers(self):
        return self.__to_int(self.hand == self.HANDS[1][0])

    def hand_is_paper(self):
        return self.__to_int(self.hand == self.HANDS[2][0])

    def __to_int(self, condition):
        return 1 if condition else 0