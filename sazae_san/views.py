from django.http import HttpResponse
from django.template import loader
from sazae_san.models import Episode
from sklearn import svm
import urllib.request
import datetime
import bs4
import re

def index(request):
    template = loader.get_template('index.html')
    episodes = __get_episodes()
    return HttpResponse(template.render({ 'episodes' : episodes }, request))

def update(request):
    __update()
    template = loader.get_template('index.html')
    episodes = __get_episodes()
    return HttpResponse(template.render(
        { 'episodes' : episodes, 'message' : '最新のデータを取得しました' },
    request))

def predict(request):
    episodes = __get_episodes()
    predicted_value = __predict(episodes)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(
        { 'episodes' : episodes, 'message' : 'じゃん！けん！「%s」！うふふふふふふ' % predicted_value },
    request))

def __get_episodes():
    return Episode.objects.order_by('-air_time')

def __update():
    for i in range(1991, datetime.date.today().year + 1):
        response = urllib.request.urlopen('http://park11.wakwak.com/~hkn/data%s.htm' % i)
        soup = bs4.BeautifulSoup(response, 'lxml')

        for content in soup.body.contents[5].contents[0].split('\n'):
            # 改行コード（<br/>）と改行タグ（\n）をスキップする
            if not (content and content.strip()):
                continue
            number, date_string, hand = content.strip().split()
            if hand == '休み':
                continue
            date = __to_date(date_string)
            try:
                Episode.objects.get(air_time = date)
                continue
            except Episode.DoesNotExist:
                hand = __remove_brackets_inner(hand)
                episode = Episode(air_time = date, hand = hand)

                episode.save()

def __to_date(date_string):
    date_string = __remove_brackets_inner(date_string)
    d = datetime.datetime.strptime(date_string, "%Y年%m月%d日")
    return datetime.date(d.year, d.month, d.day)

# ()と()内の文字を削除する
def __remove_brackets_inner(s):
    return re.sub('\(.*\)', '', s)

def __format(year):
    return int(year) + 2000 if year < 91 else int(year) + 1900

def __predict(episodes):
    data = []
    target = []
    for i in range(len(episodes) - 2):
        data.append([
            1 if episodes[i + 1].hand == Episode.HANDS[0][0] else 0,
            1 if episodes[i + 1].hand == Episode.HANDS[1][0] else 0,
            1 if episodes[i + 1].hand == Episode.HANDS[2][0] else 0,
            1 if episodes[i + 2].hand == Episode.HANDS[0][0] else 0,
            1 if episodes[i + 2].hand == Episode.HANDS[1][0] else 0,
            1 if episodes[i + 2].hand == Episode.HANDS[2][0] else 0
        ])
        target.append([episodes[i].hand])
    clf = svm.SVC(gamma=0.001, C=100.)
    clf.fit(data, target)
    return clf.predict([
            1 if episodes[0].hand == Episode.HANDS[0][0] else 0,
            1 if episodes[0].hand == Episode.HANDS[1][0] else 0,
            1 if episodes[0].hand == Episode.HANDS[2][0] else 0,
            1 if episodes[1].hand == Episode.HANDS[0][0] else 0,
            1 if episodes[1].hand == Episode.HANDS[1][0] else 0,
            1 if episodes[1].hand == Episode.HANDS[2][0] else 0
      ])[0]