new Vue({
    el: '#v-container',
    data: {
        house_id: '',
        startDate: '',
        endDate: '',
        houseData: '',
        // 存储页面的来源路径
        hrefBack: '',
        // 存储订单总额
        orderTotalPrice: '',
        // 存储订单状态
        order_status: '',
    },
    methods: {
        // 获取cookie
        getCookie: function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 获取页面的来源路径
        getReferPath: function(isAll) {
            // isAll为bool值, 确定是否获取整个域名, 默认不传, 则设为false将只截取域名后面的路径包括参数
            isAll = isAll ? isAll : false;
            refer_url = document.referrer;
            path = refer_url.replace(/((http:|https:)\/\/|\d)[^\/]*/, "");
            if (isAll) path = refer_url;
            if (!path) path = '/';
            // 返回截取后的路径, 或完整URL
            return path
        },

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

        // 计算日期之间的相差天数
        dateDiff: function (startDate, endDate) {
            /*
            * startDate为起始日期
            * endDate结束日期
            * 注意: 参数必须是'yyyy-MM-dd'类型
            */
            var aDate, oDate1, oDate2, iDays;
            aDate = startDate.split("-");
            oDate1 = new Date(aDate[1] + '-' + aDate[2] + '-' + aDate[0]);
            console.log(oDate1);
            aDate = endDate.split("-");
            oDate2 = new Date(aDate[1] + '-' + aDate[2] + '-' + aDate[0]);
            iDays = parseInt((oDate2 - oDate1) / 1000 / 60 / 60 / 24);
            // 返回: endDate-startDate 之间的相差天数
            return iDays;
        },

        // 触发时间选项
        showDate: function(idName){
            let event = window.event;
            // 适应所有的元素共用
            let v_self = this;  // 存储vue对象
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
                                    if(!v_self.startDate){
                                        alert('请选择入住日期')
                                    }else{
                                        v_self.endDate = rs.text;
                                        // 获取入住天数
                                        let days = v_self.dateDiff(v_self.startDate, v_self.endDate);
                                        if(days == 0) days = 1;
                                        // 获取订单单价
                                        let price = (v_self.houseData.price/100).toFixed(0);
                                        // 存储订单总价
                                        v_self.orderTotalPrice = (price * days);
                                    }
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
        },

        // 订单提交
        submitOrder: function(){
            let headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }

            let data = {
                house_id:   this.house_id,
                start_date: this.startDate,
                end_date:   this.endDate,
            }

            // 转json
            let jsonData = JSON.stringify(data);

            this.$http.post('/api/1.0/order/orders', jsonData, {headers: headers}).then(function(res){
                if(res.body.errcode == '0'){
                    alert('预定成功');
                    setTimeout(function(){
                        location.href = '/orders.html?order_id=' + res.body.data.order_id;
                    }, 1500);
                }else{
                    alert(res.body.errmsg);
                }
            })
        },

        // 页面初始化, 获取房屋信息
        getHouse: function(){
            this.house_id = this.decodeQuery().hid;
            this.$http.get('/api/1.0/order/house?house_id='+this.house_id).then(function(res){
                if(res.body.errcode == "4101"){
                    // 用户未登录
                    location.href = "/login.html";
                }else if(res.body.errcode == '0'){
                    this.houseData = res.body.data;
                    this.order_status = res.body.order_status;
                }else{
                    alert(res.body.errmsg);
                }
            })
        }
    },
    created: function(){

    },

    mounted: function(){
        this.hrefBack = this.getReferPath();
        this.getHouse();
    }
})
