import base
import models.post
import models.admin
import models.user

class Save(base.BaseView):
    @models.user.admin_only
    def post(self):
        conf = models.admin.SiteConfiguration.load_persist()
        conf.title = self.request.get('title').strip()
        conf.style = self.request.get('style').strip()
        conf.rss_uri = self.request.get('rss_uri').strip()
        conf.rss_description = self.request.get('rss_description').strip()
        conf.analytics_code = self.request.get('analytics_code').strip()
        conf.analytics_domain = self.request.get('analytics_domain').strip()
        conf.post_html = self.request.get('post_html').strip()
        models.admin.SiteConfiguration.save(conf)
        models.admin.Blogroll.add_by_text(self.request.get('blogrolls').strip())
        self.redirect('/c/siteconf')