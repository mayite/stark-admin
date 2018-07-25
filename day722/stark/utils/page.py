"""
分页组件使用示例：

    obj = Pagination(request.GET.get('page',1),len(USER_LIST),request.path_info)
    page_user_list = USER_LIST[obj.start:obj.end]
    page_html = obj.page_html()

    return render(request,'index.html',{'users':page_user_list,'page_html':page_html})


"""


class Pagination(object):

    def __init__(self,current_page,all_count,params,per_page_num=10,pager_count=11):
        """
        封装分页相关数据
        :param current_page: 当前页
        :param all_count:    数据库中的数据总条数
        :param per_page_num: 每页显示的数据条数
        :param base_url: 分页中显示的URL前缀
        :param pager_count:  最多显示的页码个数
        all_count；100
        per_page_num:8

        current_page   start (current_page-1)*per_page_num          end (current_page*per_page_num)
            1            0                                          8
            2            8                                          16
            3            16                                         24

         情况1：self.current_page-self.pager_count_half<1
                2
                3
                5
        pager_start=1
        pager_end=self.pager_count+1


        情况2：
        8 9 10 11 12 13 14 15 16 17 18
        15             20           25


        pager_start = self.current_page-self.pager_count_half
        pager_end = self.current_page+self.pager_count_half+1


        情况3：self.current_page+self.pager_count_half>self.all_pager
             48
             47
             79

        pager_start = self.all_pager-self.pager_count
        pager_end =self.all_pager+1


        """

        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1

        if current_page <1:
            current_page = 1

        self.current_page = current_page

        self.all_count = all_count
        self.per_page_num = per_page_num


        # 总页码
        all_pager, tmp = divmod(all_count, per_page_num)
        if tmp:
            all_pager += 1

        self.all_pager = all_pager


        self.pager_count = pager_count
        self.pager_count_half = int((pager_count - 1) / 2)  # 5
        #
        import copy
        self.params=copy.deepcopy(params)

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_num

    @property
    def end(self):
        return self.current_page * self.per_page_num

    def page_html(self):
        # 如果总页码 < 11个：
        if self.all_pager <= self.pager_count:
            pager_start = 1
            pager_end = self.all_pager + 1
        # 总页码  > 11
        else:
            # 当前页如果<=页面上最多显示11/2个页码
            if self.current_page <= self.pager_count_half:
                pager_start = 1
                pager_end = self.pager_count + 1

            # 当前页大于5
            else:
                # 页码翻到最后
                if (self.current_page + self.pager_count_half) > self.all_pager:
                    pager_start = self.all_pager - self.pager_count + 1
                    pager_end = self.all_pager + 1

                else:
                    pager_start = self.current_page - self.pager_count_half
                    pager_end = self.current_page + self.pager_count_half + 1







        #########################################################################
        page_html_list = []

        first_page = '<li><a href="?page=%s">首页</a></li>' % (1,)
        page_html_list.append(first_page)

        if self.current_page <= 1:
            prev_page = '<li class="disabled"><a href="#">上一页</a></li>'
        else:
            prev_page = '<li><a href="?page=%s">上一页</a></li>' % (self.current_page - 1,)

        page_html_list.append(prev_page)



        # self.params       {"page":7,"xxx":123}

        for i in range(pager_start, pager_end):
            self.params["page"]=i
            if i == self.current_page:
                temp = '<li class="active"><a href="?page=%s">%s</a></li>' % (i, i,)
            else:
                temp = '<li><a href="?%s">%s</a></li>' % (self.params.urlencode(), i,)
            page_html_list.append(temp)



        if self.current_page >= self.all_pager:
            next_page = '<li class="disabled"><a href="#">下一页</a></li>'
        else:
            next_page = '<li><a href="?page=%s">下一页</a></li>' % (self.current_page + 1,)
        page_html_list.append(next_page)

        last_page = '<li><a href="?page=%s">尾页</a></li>' % (self.all_pager,)
        page_html_list.append(last_page)

        return ''.join(page_html_list)