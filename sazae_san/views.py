from django.http import HttpResponse
from django.template import loader
from sazae_san.models import Episode
from sklearn import svm
import urllib.request
import datetime
import bs4

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
    response = urllib.request.urlopen('http://www.asahi-net.or.jp/~tk7m-ari/sazae_ichiran.html')
    soup = bs4.BeautifulSoup(response, 'lxml')
    for content in soup.body.contents[9].contents:
        # 改行コード（<br/>）と改行タグ（\n）をスキップする
        if not (content.string and content.string.strip()):
            continue
        number, date_string, hand = content.string.strip().split()
        if hand == '休み':
            continue
        date = __to_date(date_string)
        try:
            Episode.objects.get(air_time = date)
            continue
        except Episode.DoesNotExist:
          # （より前の部分のみ取得する
          episode = Episode(air_time = date, hand = hand.split('（')[0])
          episode.save()

def __to_date(date_string):
    year, month, day = map(int, date_string.split('.'))
    year = __format(year)
    # 実在しない日付があるので、特別に修正する
    if year == 1991 and month == 11 and day == 31:
        return datetime.date(year, month + 1, 1)
    return datetime.date(year, month, day)

def __format(year):
    return int(year) + 2000 if year < 91 else int(year) + 1900

def __predict(episodes):
    data = []
    target = []
    for i in range(len(episodes) - 2):
        data.append([
            1 if episodes[i + 1].hand ==  Episode.HANDS[0][0] else 0,
            1 if episodes[i + 1].hand ==  Episode.HANDS[1][0] else 0,
            1 if episodes[i + 1].hand ==  Episode.HANDS[2][0] else 0,
            1 if episodes[i + 2].hand ==  Episode.HANDS[0][0] else 0,
            1 if episodes[i + 2].hand ==  Episode.HANDS[1][0] else 0,
            1 if episodes[i + 2].hand ==  Episode.HANDS[2][0] else 0
        ])
        target.append([episodes[i].hand])
    clf = svm.SVC(gamma=0.001, C=100.)
    clf.fit(data, target)
    return clf.predict([
            1 if episodes[0].hand ==  Episode.HANDS[0][0] else 0,
            1 if episodes[0].hand ==  Episode.HANDS[1][0] else 0,
            1 if episodes[0].hand ==  Episode.HANDS[2][0] else 0,
            1 if episodes[1].hand ==  Episode.HANDS[0][0] else 0,
            1 if episodes[1].hand ==  Episode.HANDS[1][0] else 0,
            1 if episodes[1].hand ==  Episode.HANDS[2][0] else 0
      ])[0]