#coding=utf-8

from basic import BasicCtrl

class VoiceCtrl(BasicCtrl):
    def post(self):
        if not self.human_valid():
            self.flash(0, {'msg': '验证码错误'})
            return

        post = self.model('posts').get_by_pid(self.datum('posts'), self.input('poid'))
        if not post:
            self.flash(0, {'msg': '文章不存在'})
            return

        rank = '0'
        usid = '0'
        if self.input('auth', False) and self.current_user:
            if self.model('admin').chk_user_is_live(self.current_user):
                rank = self.get_runtime_conf('posts_talks_min_rank')
            usid = self.current_user['user_id']
            name = self.current_user['user_name']
            mail = self.current_user['user_mail']
        else:
            name = self.input('name')
            mail = self.input('mail')

        text = self.input('text')
        time = self.stime()

        try:
            self.datum('talks').invoke(
                    'insert into talks (post_id, user_ip, user_id, user_name, user_mail, talk_text, talk_rank, talk_ctms, talk_utms) values (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (post['post_id'], self.request.remote_ip, usid, name, mail, text, rank, time, time))

            self.datum('posts').invoke('update posts set post_refc = post_refc + 1 where post_id = ?', (post['post_id'],))

            self.datum('talks').commit()
            self.datum('posts').commit()

            if float(rank) > 0:
                self.flash(1, {'msg': '评论发表成功'})
            else:
                self.flash(1, {'msg': '当前评论内容暂不公开'})
        except:
            self.datum('talks').revert()
            self.datum('posts').revert()
            self.flash(0)
