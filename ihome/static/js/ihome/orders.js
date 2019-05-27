new Vue({
    el: '#v-container',
    data: {
        urlRefer: '',
        orders: [],
        order_id: '',
        order_comment: '',
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

        // 页面初始化, 获取房屋信息
        getOrders: function(){
            this.$http.get('/api/1.0/order/orders?role=customer').then(function(res){
                if(res.body.errcode == "4101"){
                    // 用户未登录
                    location.href = "/login.html";
                }else if(res.body.errcode == '0'){
                    this.orders = res.body.data.orders;
                }else{
                    alert(res.body.errmsg);
                }
            })
        },

        // 发表评价按钮触发的事件, 获取id
        commentOrPay: function(event){
            this.order_id = event.target.dataset.orderId;
        },

        // 确认评价
        affComent: function(){
            let headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            let data = {
                comment: this.order_comment,
            }
            // 转json
            let jsonData = JSON.stringify(data);

            this.$http.put('/api/1.0/order/'+this.order_id+'/comment', jsonData, {headers: headers}).then(function(res){
                if(res.body.errcode == '0'){
                    this.$refs.commentModal.style.display = 'none';
                    // 去掉遮罩层
                    let backdrop = document.querySelector('.modal-backdrop')
                    backdrop.parentNode.removeChild(backdrop);
                    document.body.className = '';
                    // 重新加载页面数据
                    this.getOrders();
                }else{
                    alert(res.body.errmsg);
                }
            });
        },

        // 确认支付
        affPay: function(event){
            this.order_id = event.target.dataset.orderId;
            let headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            this.$http.post('/api/1.0/order/'+this.order_id+'/pay', '{}', {headers: headers}).then(function(res){
                if(res.body.errcode == "4101"){
                    // 未登录
                    location.href = '/login.html';
                }else if(res.body.errcode == "0"){
                    // 然后引导用户跳转到支付链接, 新开一个窗口
                    // location.href = res.body.pay_url;
                    window.open(res.body.pay_url)

                    // 如果支付成功, 就马上查询订单状态
                    this.$http.get('/api/1.0/order/'+this.order_id+'/pay-query', '{}', {headers: headers}).then(function(res){
                        if(res.body.errcode == "0"){
                            // 如果交易成功, 则重新加载页面数据, 更新支付状态
                            this.getOrders();
                        }else{
                            alert(res.body.errmsg);
                        }
                    })
                }else{
                    alert(res.body.errmsg);
                }
            })
        }
    },
    created: function(){
        this.urlRefer = this.getReferPath();
        this.getOrders();
    },

    mounted: function(){

    }
})
