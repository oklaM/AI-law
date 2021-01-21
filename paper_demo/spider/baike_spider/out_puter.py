import os


class Outputer(object):
    def output(self, data, url):
        if data is None or url is None:
            return
        url = url.split('/')
        if '-' in url[-1]:
            outdir = os.path.join(os.getcwd(), 'outfiles', '按首字母分')
        else:
            outdir = os.path.join(os.getcwd(), 'outfiles', '按部位分')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        try:
            with open(os.path.join(outdir, url[-1] + '.txt'), 'w', encoding='utf-8') as f:
                for d in data:
                    f.write(d + '\n')
        except Exception as e:
            print('output failed:{0}'.format(e))