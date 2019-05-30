var house_data_querying = false;  // 记录是否在发送请求, 这是一个开关

var vm = new Vue({
    el: "#v-container",
    data: {
        // 存储所有的房屋信息
        initHouses: [],
        // 存储区域的对象列表
        area_obj_arr: [],
        // 动态显示日期输入框
        isShowDateInput: false,
        // 动态显示排序规则选项
        isShowFilterSort: false,
        // 存储需要的查询参数
        startDate: '',   // 入住时间
        endDate: '',     // 结束时间
        area_id: '',     // 区域id
        sort_key: '',    // 排序规则
        p: 1,            // 当前页码, 默认1
        // 存储总页数, 默认一页
        total_page: 1,
        // 接收是否存在下一页
        has_next_page: false,
    },
    methods: {
        // 解析提取url中的查询字符串参数, 如: /?key=value&key2=value2...
        decodeQuery: function (){
            var search = decodeURI(document.location.search);
            return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
                values = item.split('=');
                result[values[0]] = values[1];
                // 它返回一个对象, 如{key: value, ...} 其中key为URL参数中的键名, value为键值...
                return result;
            }, {});
        },

        // 获取城区列表
        getHouseArea: function() {
            this.$http.get('/api/1.0/house/get-area-info').then(function(res) {
                if (res.body.errcode == "0") {
                    this.area_obj_arr = res.body.data;
                } else {
                    alert(res.body.errmsg);
                }
            })
        },

        // 获取页面数据, 获取默认房屋列表
        getHouseList: function(sd='', ed='', aid='', sk='', p=''){
            // sd为起始入住时间, ed为结束入住时间
            // aid为区域编号, sk为排序规则, p为页码
            let url = '/api/1.0/house/house-list?sd='+sd+'&ed='+ed+'&aid='+aid+'&sk='+sk+'&p='+p;
            this.$http.get(url).then(function(res){
                if(res.body.errcode == "0"){
                    // 将房屋信息追加到要展示的列表中
                    this.initHouses = this.initHouses.concat(res.body.data.houses);
                    this.total_page = res.body.data.total_page;
                    this.has_next_page = res.body.data.has_next;
                }else{
                    alert(res.body.errmsg);
                }
            })
        },

        // 触发时间选项
        showDate: function(idName){
            house_data_querying = false;  // 初始化懒加载开关
            // 设置页数为第一页
            this.p = 1;
            let event = window.event;
            this.isShowDateInput = true;
            if(this.isShowDateInput){
                this.$refs.filterDate.style.display = 'block';
            }else{
                this.$refs.filterDate.style.display = 'none';
            }
            // this.$refs.filterDate.style.display = 'block';
            this.$refs.filterArea.style.display = 'none';
            this.$refs.filterSort.style.display = 'none';
            // 适应所有的元素共用
            let v_self = this;  // 存储vue对象
            if(event.target.id==idName){
                event.target.dataset.options = '{"type":"date"}';
                event.target.className += " btn mui-btn mui-btn-block";
                (function($) {
                    $.init();
                    // 绑定需要触发的元素$('id选择器')
                    btns = $('#'+idName);
                    btns.each(function(i, btn) {
                        let self = this;
                        function newBtns() {
                            let optionsJson = self.getAttribute('data-options') || '{}';
                            let options = JSON.parse(optionsJson);
                            let id = self.getAttribute('id');
                            let picker = new $.DtPicker(options);
                            picker.show(function(rs) {
                                // result.innerText = '选择结果: ' + rs.text;
                                if(event.target.tagName == 'INPUT'){
                                    // 绑定双向数据
                                    if(idName=='start-date'){
                                        v_self.startDate = rs.text;
                                    }else if(idName=='end-date'){
                                         v_self.endDate = rs.text;

                                        // 先清空房屋列表
                                        v_self.initHouses =  [];
                                        // 发送新请求, 获取页面
                                        v_self.getNewHouseList()
                                        // 隐藏输入框
                                        v_self.isShowDateInput = false;
                                        v_self.$refs.filterDate.style.display = 'none';
                                    }
                                }else{
                                    event.target.innerText =  rs.text;
                                }

                                picker.dispose();
                            });
                        }
                        btn.addEventListener('tap', newBtns(), false);
                    });
                })(mui);

                /*** 可为确认按钮, 设置额外的自定义点击事件 ***/
                // 获取遮罩层与确认按钮
                muiBackdrop = document.querySelector('.mui-backdrop');
                muiBackdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
            }
        },

        // 触发区域选项
        showArea: function(){
            house_data_querying = false;  // 初始化懒加载开关
            // 设置页数为第一页
            this.p = 1;
            let event = window.event;
            this.$refs.filterArea.style.display = 'block';
            // this.$refs.displayMask.style.display = 'block';
            this.$refs.filterDate.style.display = 'none';
            this.$refs.filterSort.style.display = 'none';

            let get_area_objs = [];
            let aid = '';
            let aname = '';
            let obj = {};
            for(let i in this.area_obj_arr){
                aid = this.area_obj_arr[i].aid;
                aname = this.area_obj_arr[i].aname;
                obj = {value:aid , text:aname};
                get_area_objs.push(obj)
            }
            let v_self = this;  // 存储vue对象
            (function($) {
                $.init();
                $.ready(function() {
                    //普通示例
                    var userPicker = new $.PopPicker();
                    userPicker.setData(get_area_objs);
                    // var showUserPickerButton = doc.getElementById(idName);
                    var showUserPickerButton = event.target;
                    function newAreas(event){
                        userPicker.show(function(items) {
                            v_self.area_id = items[0].value;
                            // console.log('执行了');
                            v_self.initHouses =  [];
                            v_self.getNewHouseList()
                        });
                    }
                    showUserPickerButton.addEventListener('tap', newAreas(), false);
                });
            })(mui);

            /*** 可为确认按钮, 设置额外的自定义点击事件 ***/
            // 获取遮罩层与确认按钮
            muiBackdrop = document.querySelector('.mui-backdrop');
            muiBackdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';

        },

        // 显示排序规则按钮
        showSort: function(){
            this.isShowFilterSort =! this.isShowFilterSort;
            if(this.isShowFilterSort){
                this.$refs.filterSort.style.display = 'block';
            }else{
                this.$refs.filterSort.style.display = 'none';
            }
            this.$refs.displayMask.style.display = 'block';
            this.$refs.filterDate.style.display = 'none';
            this.$refs.filterArea.style.display = 'none';
        },

        // 触发排序规则
        setHouseSort: function(event){
            house_data_querying = false;  // 初始化懒加载开关
            // 先清空房屋列表
            this.initHouses =  [];
            // 设置页数为第一页
            this.p = 1;
            sortList = Array.from(this.$refs.filterSort.children);
            for(let item of sortList){
                if(item == event.target){
                    event.target.className = 'active';
                    // 设置排序规则到请求参数中
                    this.sort_key = event.target.dataset.skey;
                    // 发送请求
                    this.getNewHouseList();
                    this.isShowFilterSort = false;
                    this.$refs.filterSort.style.display = 'none';
                    this.$refs.displayMask.style.display = 'none';
                }else{
                    item.className = '';
                }
            }
        },

        // 获取新的房屋列表, 这也是自定义遮罩层控制的事件
        getNewHouseList: function(){
            this.$refs.filterSort.style.display = 'none';
            this.$refs.filterArea.style.display = 'none';
            this.$refs.filterDate.style.display = 'none';
            this.$refs.displayMask.style.display = 'none';

            // 设置查询参数
            let sd = this.startDate;
            let ed = this.endDate;
            let aid = this.area_id;
            if(!aid){
                if(this.decodeQuery().aid){
                    aid = this.decodeQuery().aid;
                }
            }
            let sk = this.sort_key;
            let p = this.p;

            // 发送请求获取新页面
            this.getHouseList(sd, ed, aid, sk, p);
        },

    },
    created: function(){
        this.getHouseArea();
        // 当从首页跳转到搜索页面时, 初始化加载页面
        let url_params = this.decodeQuery();
        if(!url_params.sd) url_params.sd = '';
        if(!url_params.aid) url_params.aid = '';
        this.getHouseList(sd=url_params.sd, ed='', aid=url_params.aid);
    },
    // mounted: function(){
    //     this.getHouseList();
    // }
})


/*** 操控页面懒加载 ***/
window.onscroll = function() {
    // 获取窗口高度
    var windowHeight = window.innerHeight;
    // 获取文档对象
    var element = document.documentElement;
    // 获取文档可见区域的高度
    var a = element.scrollTop == 0 ? document.body.clientHeight : element.clientHeight;
    // 获取已从上往下滚动不见区域的高度
    var b = element.scrollTop == 0 ? document.body.scrollTop : element.scrollTop;
    // 获取文档整体高度
    var c = element.scrollTop == 0 ? document.body.scrollHeight : element.scrollHeight;

    // 获取是否有下一页
    let has_next = vm.$root.has_next_page;
    // 获取当前页码默认值
    let page = vm.$root.p;
    // 获取总页数
    let total_page = vm.$root.total_page;

    // 如果滚动条距离最底部不足1px
    if ((c - b) < windowHeight + 2) {
        // 必须在没有记录的情况下才发送
        if(!house_data_querying){
            if(page < total_page){
                // 将当前页数+1
                vm.$root.p += 1;
                // 向后端发送请求，查询下一页房屋数据
                vm.$root.getNewHouseList();
            } else {
                house_data_querying = true;
            }
        }
    }
}
