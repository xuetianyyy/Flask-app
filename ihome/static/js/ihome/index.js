var vm = new Vue({
    el: "#v-container",
    data: {
        // 存放最热门的房屋对象列表
        houses: [],
        // 轮播用
        sliderItems: [],
        sliderItemslength: 1,
        // 存储区域的对象列表
        area_obj_arr: [],
        // 房屋详情信息页面地址, 注意:　它是缺少参数值的
        house_detail_url: '/detail.html?house_id=',
    },
    methods: {
        // 获取用户登录状态
        getUserLogin: function() {
            this.$http.get("/api/1.0/user/session").then(function(res) {
                if (res.body.errcode == "0") {
                    this.$refs.userInfo.children[1].innerHTML = res.body.data.name;
                    this.$refs.userInfo.style.cssText = "display:block;";
                } else {
                    this.$refs.registerLogin.style.cssText = "display:block;";
                }
            })
        },

        // 获取首页幻灯片
        getIndexImage: function() {
            this.$http.get('/api/1.0/house/index').then(function(res) {
                // console.log(res);
                if (res.body.errcode == "0") {
                    // 证明获取的不是字符串, 而是对象
                    this.houses = res.body.data;
                    // console.log(this.houses);
                } else {
                    alert(res.body.errmsg);
                }
            })
        },

        // 自动设置轮播窗口的高度
        setSliderHeigt: function() {
            this.$refs.swiperContainer.style.height = this.$refs.swiperContainer.offsetWidth * 0.8 + 'px';
        },
        // 设置轮播
        setSlider: function() {
            let xtSliderLength = this.$refs.swiperContainer.children.length;
            if (this.sliderItemslength >= xtSliderLength) {
                this.sliderItemslength = 0;
            }
            let self = this;
            Array.from(self.$refs.swiperContainer.children).forEach(function(item, index) {
                if (index != self.sliderItemslength) {
                    item.style.cssText = "right: -100%; display: none;";
                    item.style.right = '-100%';
                } else {
                    item.style.cssText = "right: 0; display: block;";
                }
            });
            this.sliderItemslength += 1;
        },

        // 获取城区列表
        getMyHouse: function() {
            this.$http.get('/api/1.0/house/get-area-info').then(function(res) {
                if (res.body.errcode == "0") {
                    this.area_obj_arr = res.body.data;
                } else {
                    alert(res.body.errmsg);
                }
            })
        },

        // 基于Vue的事件封装, 显示日期选项
        showDate: function (event){
            // 生成日期选择, 适应所有的元素共用, 但必须是元素id == idName的元素才会被触发
            event.target.dataset.options = '{"type":"date"}';       // 动态设置元素的自定义属性, 必须
            event.target.className += " btn mui-btn mui-btn-block"; // 动态追加元素的样式, 必须
            let v_root = this;
            (function($) {
                $.init();
                // 绑定需要触发的元素$('id选择器')
                let result = v_root.$refs.timeResult;
                btns = $('#showTimeDate');
                btns.each(function(i, btn) {
                    let self = this;
                    function newBtns() {
                        let optionsJson = self.getAttribute('data-options') || '{}';
                        let options = JSON.parse(optionsJson);
                        let id = self.getAttribute('id');
                        let picker = new $.DtPicker(options);
                        picker.show(function(rs) {
                            result.innerText = rs.text;
                            // 资源回收
                            picker.dispose();
                        });
                    }
                    btn.addEventListener('tap', newBtns(), false);
                });
            })(mui);

            // 获取遮罩层与确认按钮, 设置颜色加深, 默认颜色较浅
            muiBackdrop = document.querySelector('.mui-backdrop');
            muiBackdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        },

        // 基于vue的封装, 地区选择器
        showArea: function(event){
            event.target.dataset.options = '{"type":"date"}';       // 动态设置元素的自定义属性, 必须
            event.target.className += " btn mui-btn mui-btn-block"; // 动态追加元素的样式, 必须
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
                            console.log(v_self.$refs.areaResult);
                    function newAreas(){
                        userPicker.show(function(items) {
                            // v_self.area_id = items[0].value;
                            v_self.$refs.areaResult.innerText = items[0].text;
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

        // 搜索列表, 设置链接
        searchHouse: function(){
            let areaResult = this.$refs.areaResult.innerText;
            let area_id = this.$refs.areaResult.dataset.aid;
            let start_date = this.$refs.timeResult.innerText;
            if(areaResult == '选择城区' && start_date == '入住日期'){
                // alert('请选择城区和入住时间');
                location.href = '/search.html';
            }else if(areaResult == '选择城区' && start_date != '入住日期'){
                location.href = '/search.html?sd=' + start_date;
            }else if(areaResult != '选择城区' && start_date == '入住日期'){
                location.href = '/search.html?aid=' + area_id;
            }else{
                location.href = '/search.html?sd=' + start_date + '&aid=' + area_id;
            }
        },
    },
    mounted: function() {
        // 执行获取登录状态
        this.getUserLogin()
        this.getIndexImage()
        // 轮播
        this.setSliderHeigt()
        window.addEventListener('resize', this.setSliderHeigt)
        let self = this;
        setInterval(function() {
            self.setSlider()
        }, 3000);
        this.getMyHouse();
    },
    updated: function(){
        // 初始化显示
        this.$refs.swiperContainer.children[0].style.cssText = "right: 0; display: block;";
    }
})



