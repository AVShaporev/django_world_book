from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AuthorsForm
from django.http import *
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.

def index(request):
    # Генерация количеств некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instance = BookInstance.objects.all().count()

    # Доступныем книги статус - "На складе"
    # Здесь метод all() применен по умолчнаию
    num_instance_aviable = BookInstance.objects.filter(status=2).count()

    # Авторы книг
    num_authors = Author.objects.all().count()

    # количеством посещений этого view, посчитанное в переменной
    # session
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Отрисовка HTML шаблона index.html с данными    
    # внутри переменной context
    return render(request, 'index.html',
                  context={'num_books': num_books,
                           'num_instance': num_instance,
                           'num_instance_available': num_instance_aviable,
                           'num_authors': num_authors,
                           'num_visits': num_visits})

class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'    
    success_url = reverse_lazy('books')

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')   

class BookListView(generic.ListView):
    model = Book
    paginate_by = 3

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 3

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    '''
    Универсальный класс предсатвления списка книг,
    находящихся в заказе у текущего пользователя.
    '''
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user).filter(
            status='2').order_by('due_back')
    
# Получение данных из БД и загрузка шаблона authors_add.html
def authors_add(request):
    author = Author.objects.all()
    authorsform = AuthorsForm()
    return render(request, "catalog/authors_add.html",
                  {"form": authorsform, "author": author})

# Сохранение данных об авторах в БД
def create(request):
    if request.method == 'POST':
        author = Author()
        author.first_name = request.POST.get("first_name")
        author.last_name = request.POST.get("last_name")
        author.date_of_birth = request.POST.get("date_of_birth")
        author.date_of_death = request.POST.get("date_of_death")
        author.save()
        return HttpResponseRedirect("/authors_add")
    
# удалние авторов из БД
def delete(request, id):
    try:
        author = Author.objects.get(id=id)
        author.delete()
        return HttpResponseRedirect("/authors_add")
    except Author.DoesNotExist:
        return HttpResponseNotFound("<h2>Автор не найден!</h2>")
    
def edit1(request, id):
    author = Author.objects.get(id=id)
    if request.method == 'POST':
        author.first_name = request.POST.get("first_name")
        author.last_name = request.POST.get("last_name")
        author.date_of_birth = request.POST.get("date_of_birth")
        author.date_of_death = request.POST.get("date_of_death")
        author.save()
        return HttpResponseRedirect("/authors_add")
    else:
        return render(request, "edit1.html", {"author": author})