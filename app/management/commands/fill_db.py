from django.core.management.base import BaseCommand
from app.models import Question, Profile, Label, Answer, Score
from django.contrib.auth.models import User

from faker import Faker
import random

DEFAULT_N_USERS = 1
DEFAULT_N_QUESTIONS = 10
DEFAULT_N_ANSWERS = 100
DEFAULT_N_LABELS = 1
DEFAULT_N_SCORES = 200

CHAR_LIST = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
             't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker()

    def add_arguments(self, parser):
        parser.add_argument('--ratio', type=int)

    def handle(self, *args, **options):
        ratio = int(options['ratio']) if options['ratio'] else 10

        self.users_gen(ratio * DEFAULT_N_USERS)
        self.labels_gen(ratio * DEFAULT_N_LABELS)
        self.questions_gen(ratio * DEFAULT_N_QUESTIONS)
        self.answers_gen(ratio * DEFAULT_N_ANSWERS)
        self.scores_gen(ratio * DEFAULT_N_SCORES)

    def users_gen(self, count):
        print("Users generating...")
        users = [None] * count
        profiles = [None] * count

        for i in range(count):
            user = User(username=self.faker.unique.user_name(), first_name=self.faker.first_name(),
                        last_name=self.faker.last_name(), email=self.faker.email())
            user.set_password(raw_password=self.faker.password())

            users[i] = user
            profiles[i] = Profile(user=user, avatar=f'/gen_avatars/avatar-{random.randint(1, 9)}.jpg')
        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)
        print('Success.')

    @staticmethod
    def labels_gen(count):
        print("labels generating...")
        word = [None] * 6
        labels = [None] * count
        used_words = []
        for i in range(count):
            print(i)
            for j in range(6):
                word[j] = random.choice(CHAR_LIST)
            while word in used_words:
                for j in range(6):
                    word[j] = random.choice(CHAR_LIST)
            used_words.append(word.copy())

            labels[i] = Label(name="".join(word))

        Label.objects.bulk_create(labels)
        print("Success.")

    def questions_gen(self, count):
        print("Questions generating...")
        prof_min_id = Profile.objects.order_by('id')[0].id
        prof_max_id = Profile.objects.order_by('-id')[0].id
        label_min_id = Label.objects.order_by('id')[0].id
        label_max_id = Label.objects.order_by('-id')[0].id

        questions = [None] * count
        for i in range(count):
            print(i)
            title = self.faker.paragraph(1)[:-1] + '?'
            text = self.faker.paragraph(random.randint(5, 20))
            profile_id = random.randint(prof_min_id, prof_max_id)

            questions[i] = Question(text=text, title=title, profile_id=profile_id)
        questions = Question.objects.bulk_create(questions)
        print("Success.")

        print("Adding labels to questions...")
        labels = [None] * 10
        for i in range(count):
            print(i)
            n_labels = random.randint(1, 5)
            for j in range(n_labels):
                labels[j] = Label.objects.get(id=random.randint(label_min_id, label_max_id))
            questions[i].labels.add(*labels[:n_labels])
            questions[i].save()
        print("Success.")

    def answers_gen(self, count):
        print("Answers generating...")
        prof_min_id = Profile.objects.order_by('id')[0].id
        prof_max_id = Profile.objects.order_by('-id')[0].id
        que_min_id = Question.objects.order_by('id')[0].id
        que_max_id = Question.objects.order_by('-id')[0].id

        answers = [None] * count
        for i in range(count):
            print(i)
            text = self.faker.paragraph(random.randint(5, 20))
            profile_id = random.randint(prof_min_id, prof_max_id)
            question_id = random.randint(que_min_id, que_max_id)

            answers[i] = Answer(text=text, profile_id=profile_id, question_id=question_id)
        Answer.objects.bulk_create(answers)
        print("Success.")

    @staticmethod
    def scores_gen(count):
        prof_min_id = Profile.objects.order_by('id')[0].id
        prof_max_id = Profile.objects.order_by('-id')[0].id
        que_min_id = Question.objects.order_by('id')[0].id
        que_max_id = Question.objects.order_by('-id')[0].id

        n_q_likes = count // 4
        q_likes = [None] * n_q_likes
        used_pairs = []
        print('Question likes generating...')
        for j in range(n_q_likes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            question_id = random.randint(que_min_id, que_max_id)
            while (profile_id, question_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                question_id = random.randint(que_min_id, que_max_id)
            used_pairs.append((profile_id, question_id))

            question = Question.objects.get(id=question_id)
            question.rating += 1
            question.save()

            q_likes[j] = Score(score_value=1, profile_id=profile_id, content_object=question)
        Score.objects.bulk_create(q_likes)
        print("Success.")

        n_q_dislikes = count // 4
        q_dislikes = [None] * n_q_dislikes
        print('Question dislikes generating...')
        for j in range(n_q_dislikes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            question_id = random.randint(que_min_id, que_max_id)
            while (profile_id, question_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                question_id = random.randint(que_min_id, que_max_id)
            used_pairs.append((profile_id, question_id))

            question = Question.objects.get(id=question_id)
            question.rating -= 1
            question.save()

            q_dislikes[j] = Score(score_value=-1, profile_id=profile_id, content_object=question)
        Score.objects.bulk_create(q_dislikes)
        print("Success.")

        # --------------------------Answers generating------------------------------
        ans_min_id = Answer.objects.order_by('id')[0].id
        ans_max_id = Answer.objects.order_by('-id')[0].id

        n_a_likes = count // 4
        a_likes = [None] * n_a_likes
        used_pairs = []
        print("Answer likes generating...")
        for j in range(n_a_likes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            answer_id = random.randint(ans_min_id, ans_max_id)
            while (profile_id, answer_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                answer_id = random.randint(ans_min_id, ans_max_id)
            used_pairs.append((profile_id, answer_id))

            answer = Answer.objects.get(id=answer_id)
            answer.rating += 1
            answer.save()

            a_likes[j] = Score(score_value=1, profile_id=profile_id, content_object=answer)
        Score.objects.bulk_create(a_likes)
        print("Success.")

        n_a_dislikes = count - n_a_likes * 3
        a_dislikes = [None] * n_a_dislikes
        print("Answer dislikes generating...")
        for j in range(n_a_dislikes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            answer_id = random.randint(ans_min_id, ans_max_id)
            while (profile_id, answer_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                answer_id = random.randint(ans_min_id, ans_max_id)
            used_pairs.append((profile_id, answer_id))

            answer = Answer.objects.get(id=answer_id)
            answer.rating -= 1
            answer.save()

            a_dislikes[j] = Score(score_value=-1, profile_id=profile_id, content_object=answer)
        Score.objects.bulk_create(a_dislikes)
        print("Success.")
