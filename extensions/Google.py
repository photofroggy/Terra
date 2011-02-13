
import re
import json
import urllib.parse
import urllib.request
from terra import extension

class Extension(extension.API):
    
    # Configure the extension!
    about = 'Use this extension to search google from dAmn!'
    version = 1
    author = 'photofroggy'
    # search_url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}&rsz={1}'
    referer = 'http://chat.deviantart.com/chat/#channel'
    
    def init(self):
        """Further extension configuration."""
        self.bind(self.c_google, 'command', ['google'], 'Web search engine, powered by google!')
    
    def c_google(self, cmd, dAmn):
        query = cmd.arguments(1, True)
        nums = cmd.arguments(1)
        if not nums.isdigit(): nums = 2
        else:
            query = query.replace(nums, '').strip()
            nums = int(nums)
            nums = 1 if nums < 1 else (nums if nums <= 8 else 8)
        if not query:
            self.__no_query(cmd.ns, cmd.user, dAmn)
            return
        response = self.search(query, nums, dAmn)
        if response['responseStatus'] != 200:
            dAmn.say(cmd.ns, cmd.user+': An error occured! Error: '+response['responseDetails'])
            return
        if not response['responseData']['results']:
            dAmn.say(cmd.ns, cmd.user+': No results were found.')
            return
        dAmn.say(cmd.ns, '<abbr title="'+cmd.user+'"></abbr>:magnify: '+self.format_web(query, response, nums))
    
    def __no_query(self, ns, user, dAmn):
        trigger = self.ccore.info.trigger
        help = user+': To use this command, use the syntax <b>'+trigger+'google [query]</b>, eg:'
        help+= ' <b>'+trigger+'google search query</b>'
        help+= '<br/><sub>-- You can define the number of results to display using the syntax <b>'
        help+= trigger+'google [results] [query]</b>, eg:'
        help+= ' <b>'+trigger+'google 3 search query</b>.<br/>-- Only <b><i>8</i></b> '
        dAmn.say(ns, help + 'results can be displayed at once.</sub>')
    
    def search(self, q='Example%20Query', rsz=2, dAmn=None):
        """Send search query to google.com and return response."""
        rsz = 'small' if rsz <= 4 else 'large'
        opener = urllib.request.build_opener()
        req = urllib.request.Request(
            urls.web.format(urllib.parse.quote(q), rsz),
            None,
            {'Accept-Language': 'en-us,en;q=0.5',
                'User-Agent': dAmn.agent,
                'Referer': self.referer},
        )
        try:
            url = opener.open(req)
            data = url.read().decode('utf-8', 'ignore')
            data = '{'+re.findall('\{(.*)\}', data)[0]+'}'
            return json.loads(data)
        except Exception as e:
            dAmn.logger('~Global', 'Search Error: '+e.args[0], showns=False)
            return {'responseStatus': 0, 'responseDetails': e.args[0]}
    
    def format_web(self, query, response, rsz):
        """Format web search results for output!"""
        if rsz > len(response['responseData']['results'])+1:
            rsz = len(response['responseData']['results'])+1
        rszstr = 's <b><em>1 to {0}</em></b>'.format(str(rsz)) if rsz != 1 else ' 1'
        head = 'Search result{0}'.format(rszstr)
        head+= ' of <b><em>{0}</em></b> for <b><em>{1}</em></b>:<ol>'.format(response['responseData']['cursor']['estimatedResultCount'],
            query)
        rsstr = [head]
        for index, result in enumerate(response['responseData']['results']):
            if index == rsz: break
            rsstr.append('<br/>'.join([
                '<li><a href="{0}">{1}</a>'.format(result['url'], result['titleNoFormatting']),
                result['content'],
                '<sup><code>{0}</code> - <a href="{1}">Cache</a></sup></li>'.format(result['url'], result['cacheUrl'])
            ]))
        rsstr = (''.join(rsstr)) + '</ol><a href="{0}">More results from google...</a>'
        return rsstr.format(response['responseData']['cursor']['moreResultsUrl'])

class urls:
    web = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}&rsz={1}'
    
# EOF
