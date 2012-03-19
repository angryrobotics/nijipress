from google.appengine.ext import db
from google.appengine.api import memcache

import util
import tag

class Post(db.Model):
    pid = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty(multiline=False)
    content = db.TextProperty()

    def init_tags(self, tags):
        self.tags = tags
        return self

def new():
    p = Post()
    p.title = ''
    p.tags = []
    p.content = ''
    posts = db.GqlQuery('SELECT * FROM Post ORDER BY pid DESC')
    if posts.count() == 0:
        p.pid = 0
    else:
        p.pid = posts[0].pid + 1
    return p

def fetch(page=0, count=util.ITEMS_PER_PAGE):
    if page == 0:
        return _first_page_posts(count)
    return [post.init_tags(tag.tags_by_post_id(post.pid)) for post in
       db.GqlQuery('SELECT * FROM Post ORDER BY date DESC').fetch(count,
                                                                  count * page)]

def count_pages():
    return util.count_pages(db.GqlQuery('SELECT __key__ FROM Post').count())

def count_pages_by_tag(t):
    return util.count_pages(
          db.GqlQuery('SELECT __key__ FROM TagPostR WHERE tag = :1', t).count())

def by_id(ident):
    post_id = int(ident)
    posts = db.GqlQuery('SELECT * FROM Post WHERE pid = :1', post_id)
    if posts.count() == 0:
        raise ValueError('no such post')
    return posts[0].init_tags(tag.tags_by_post_id(post_id))

def by_tag(t, page=0, count=util.ITEMS_PER_PAGE):
    post_ids = [r.post_id for r in
                      db.GqlQuery('SELECT * FROM TagPostR WHERE tag = :1', t)]
    return [post.init_tags(tag.tags_by_post_id(post.pid)) for post in
                        db.Query(Post).filter('pid in', post_ids).order('-date')
                                    .fetch(count, count * page)]

def put(post, tags):
    post.put()
    _invalidate_cache()
    tag.update_relations(post.pid, tags)

def _invalidate_cache():
    memcache.delete('posts')
    memcache.delete('tags')

def _first_page_posts(count):
    cache = memcache.get('posts')
    if cache == None:
        cache = _load_cache()
        memcache.set('posts', cache)
    return cache[0: count]

def _load_cache():
    return [p.init_tags(tag.tags_by_post_id(p.pid))
            for p in db.GqlQuery('SELECT * FROM Post ORDER BY date DESC').
                                                 fetch(util.ITEMS_PER_PAGE)]