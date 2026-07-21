"""
Models for courses, chapters, lessons, exercises and quizzes.
"""
from django.db import models
from django.conf import settings
import uuid


class Chapter(models.Model):
    """
    A chapter contains multiple lessons organized by order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    order_index = models.IntegerField(default=0, db_index=True)
    estimated_duration = models.IntegerField(help_text="Estimated duration in minutes")

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses_chapter'
        ordering = ['order_index']
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'

    def __str__(self):
        return f"{self.order_index}. {self.title}"

    @property
    def lesson_count(self):
        """Return the number of lessons in this chapter."""
        return self.lessons.count()


class Lesson(models.Model):
    """
    A lesson can be theory content, an exercise, or a quiz.
    """
    LESSON_TYPES = [
        ('THEORY', 'Théorie'),
        ('EXERCISE', 'Exercice'),
        ('QUIZ', 'Quiz'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='THEORY')
    order_index = models.IntegerField(default=0, db_index=True)

    # Theory content (Markdown)
    content = models.TextField(blank=True, help_text="Markdown content for theory lessons")

    # Video URL (optional)
    video_url = models.URLField(blank=True, null=True)

    estimated_duration = models.IntegerField(default=10, help_text="Estimated duration in minutes")
    points = models.IntegerField(default=10, help_text="Points awarded for completion")

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses_lesson'
        ordering = ['chapter__order_index', 'order_index']
        unique_together = ['chapter', 'slug']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        indexes = [
            models.Index(fields=['chapter', 'order_index']),
            models.Index(fields=['lesson_type']),
        ]

    def __str__(self):
        return f"{self.chapter.order_index}.{self.order_index} - {self.title}"


class Exercise(models.Model):
    """
    Coding exercise with starter code and automated tests.
    """
    DIFFICULTY_LEVELS = [
        ('EASY', 'Facile'),
        ('MEDIUM', 'Moyen'),
        ('HARD', 'Difficile'),
    ]

    LANGUAGES = [
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('javascript', 'JavaScript'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='exercise')

    instructions = models.TextField(help_text="Exercise instructions in Markdown")
    starter_code = models.TextField(help_text="Initial code template")
    solution = models.TextField(help_text="Reference solution (hidden from students)")
    language = models.CharField(max_length=20, choices=LANGUAGES, default='html')

    # Tests stored as JSONB
    tests = models.JSONField(
        default=list,
        help_text="List of test cases with name, code, and points"
    )

    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='MEDIUM')
    max_attempts = models.IntegerField(default=0, help_text="0 = unlimited")
    time_limit = models.IntegerField(default=300, help_text="Time limit in seconds for code execution")

    # Hints
    hints = models.JSONField(
        default=list,
        help_text="List of hints (progressive help)",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses_exercise'
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'

    def __str__(self):
        return f"Exercise: {self.lesson.title}"

    @property
    def total_points(self):
        """Calculate total points from all tests."""
        return sum(test.get('points', 0) for test in self.tests)


class Quiz(models.Model):
    """
    Multiple choice quiz with questions and answers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')

    instructions = models.TextField(blank=True, help_text="Quiz instructions")

    # Questions stored as JSONB
    questions = models.JSONField(
        default=list,
        help_text="List of questions with type, text, options, correct_answer, points"
    )

    passing_score = models.IntegerField(default=70, help_text="Minimum percentage to pass")
    time_limit = models.IntegerField(default=0, help_text="Time limit in minutes, 0 = unlimited")
    max_attempts = models.IntegerField(default=3, help_text="0 = unlimited")

    randomize_questions = models.BooleanField(default=False)
    randomize_options = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses_quiz'
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"Quiz: {self.lesson.title}"

    @property
    def total_points(self):
        """Calculate total points from all questions."""
        return sum(q.get('points', 1) for q in self.questions)

    @property
    def question_count(self):
        """Return the number of questions."""
        return len(self.questions)


class Project(models.Model):
    """
    Final project for a chapter or module.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='projects')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()

    requirements = models.TextField(help_text="Project requirements in Markdown")
    starter_files = models.JSONField(
        default=dict,
        help_text="Starter files structure",
        blank=True
    )

    evaluation_criteria = models.JSONField(
        default=list,
        help_text="List of evaluation criteria with points"
    )

    deadline_days = models.IntegerField(default=7, help_text="Days allowed to complete")
    points = models.IntegerField(default=100)

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses_project'
        ordering = ['chapter__order_index']
        unique_together = ['chapter', 'slug']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"Project: {self.title}"
