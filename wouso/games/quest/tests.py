from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from wouso.core import scoring
from wouso.core.qpool.models import Question, Answer, Category
from models import *
from wouso.core.scoring import Coin
from wouso.core.tests import WousoTest
from wouso.core.user.models import Race

class QuestTestCase(TestCase):
    def setUp(self):
        self.user, new = User.objects.get_or_create(username='_test')
        self.user.save()
        profile = self.user.get_profile()
        self.quest_user = profile.get_extension(QuestUser)
        scoring.setup_scoring()

    def tearDown(self):
        #self.user.delete()
        pass

    def check_answer_test(self):
        cat = Category.objects.create(name='quest')
        question = Question.objects.create(text='test_q', answer_type='F',
                                           category=cat, active=True)
        answer1 = Answer.objects.create(text='test_a1', correct=True, question=question)
        answer2 = Answer.objects.create(text='test_a2', correct=True, question=question)

        start = datetime.datetime.now()
        end = datetime.datetime.now() + timedelta(days=1)
        quest = Quest.objects.create(start=start, end=end)

        quest.questions.add(question)

        self.assertEqual(quest.count, 1)

        self.quest_user.current_quest = quest

        quest.check_answer(self.quest_user, 'Test_a2')

        self.assertTrue(self.quest_user.finished)


class FinalQuestTestCase(WousoTest):
    def test_final_bonus(self):
        u1 = self._get_player(1).get_extension(QuestUser)
        u2 = self._get_player(2).get_extension(QuestUser)
        r = Race.objects.create(name='rasa_buna', can_play=True)
        Formula.objects.create(id='finalquest-ok', formula='points=50*({level}+1)/{level_users}')
        Formula.objects.create(id='level-gold', formula='gold=0')
        Coin.objects.create(id='points')
        Coin.objects.create(id='gold')
        final = FinalQuest.objects.create(start=datetime.datetime.now(), end=datetime.datetime.now())
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)
        question = Question.objects.create(text='test', answer_type='F')
        final.questions.add(question)

        u1.current_level = 1; u1.race = r
        u1.save()
        u2.current_level = 1; u2.race = r
        u2.save()
        final.give_level_bonus()
        u1 = QuestUser.objects.get(pk=u1.pk)
        self.assertEqual(u1.points, 50)
        u2 = QuestUser.objects.get(pk=u2.pk)
        self.assertEqual(u2.points, 50)