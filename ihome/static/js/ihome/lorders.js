new Vue({
    el: '#v-container',
    data: {
        order_id: '',
        orders: [],
        // 拒单原因
        rejectReason: '',
    },
    methods: {
        // 获取cookie
        getCookie: function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
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
            this.$http.get('/api/1.0/order/orders?role=landlord').then(function(res){
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

        // 接单或拒绝按钮触发
        acceptOrReject: function(event){
            // 获取触发的订单id
            this.order_id = event.target.dataset.orderid;
        },

        // 确认接单事件
        acceptOrder: function(){
            let headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }

            // json
            let jsonData = '{"action": "accept"}';

            this.$http.put('/api/1.0/order/'+this.order_id+'/status', jsonData, {headers: headers}).then(function(res){
                if(res.body.errcode == '0'){
                    // alert('接单成功');
                    this.$refs.acceptModal.style.display = 'none';
                    // 去掉遮罩层
                    let backdrop = document.querySelector('.modal-backdrop')
                    backdrop.parentNode.removeChild(backdrop);
                    document.body.className = '';
                    // 重新获取页面数据
                    this.getOrders();
                }else{
                    alert(res.body.errmsg);
                }
            })
        },

        // 确认拒单事件
        rejectOrder: function(){
            let headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            let data = {
                action: "reject",
                reason: this.rejectReason,
            }
            // 转json
            let jsonData = JSON.stringify(data);

            this.$http.put('/api/1.0/order/'+this.order_id+'/status', jsonData, {headers: headers}).then(function(res){
                if(res.body.errcode == '0'){
                    this.$refs.rejectModal.style.display = 'none';
                    // 去掉遮罩层
                    let backdrop = document.querySelector('.modal-backdrop')
                    backdrop.parentNode.removeChild(backdrop);
                    document.body.className = '';
                    // 重新获取页面数据
                    this.getOrders();
                }else{
                    alert(res.body.errmsg);
                }
            });
        },
    },
    created: function(){
        this.getOrders();
    },

    mounted: function(){

    }
})
