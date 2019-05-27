var vm = new Vue({
    el: "#v-container",
    data: {
        // 存储用户房屋列表
        houses: [],
        // 房屋详情信息页面地址, 注意:　它是缺少参数值的
        house_detail_url: '/detail.html?house_id=',
    },

    methods: {
        getUserAuth: function(){
           this.$http.get('/api/1.0/user/get-real-name').then(function(res){
                if(res.body.errcode == "4101"){
                    // 用户未登录
                    location.href = "/login.html";
                }else if(res.body.errcode == "0"){
                    id_card = res.body.data.id_card;
                    real_name = res.body.data.real_name;
                    if(id_card && real_name){
                        // 显示用户发布房源
                        this.$refs.housesList.style.cssText = "display: block"
                        this.$http.get('/api/1.0/house/user-house').then(function(res){
                            if(res.body.errcode == "0"){
                                // 得到个人房屋对象列表
                                this.houses = res.body.data.houses;
                            }else{
                                alert(res.body.errmsg)
                            }
                        })
                    }else{
                        this.$refs.authWarn.style.cssText = "display: block"
                        this.$refs.housesList.style.cssText = "display: none"
                    }
                }else{
                    alert(res.body.errmsg)
                }
           })
        },
    },
    mounted: function(){
        this.$nextTick(function(){
            this.getUserAuth()
            console.log(this.houses.length)
        })

    },
})


