new Vue({
    el: "#v-container",
    data: {
        realName: null, // 真实姓名
        idCard: null,   // 身份证号
        req: /\d{17}[\dX]/g, // 身份证号验证
    },
    methods: {
        // 获取cookie
        getCookie: function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 获取用户实名信息
        getRealName: function(){
            this.$http.get('/api/1.0/user/get-real-name').then(function(res){
                if(res.body.errcode == "4101"){
                    // 用户未登录
                    location.href = "/login.html";
                }else if(res.body.errcode == "0"){
                    this.realName = res.body.data.real_name;
                    this.idCard = res.body.data.id_card;
                    // 如果实名已经认证, 禁用所有按钮功能
                    this.$refs.realName.disabled = true;
                    this.$refs.idCard.disabled = true;
                    this.$refs.btnSuccess.disabled = true;
                    // 如果用户没有设置过实名
                    if(!this.realName){
                        this.$refs.errorMsg.children[0].innerHTML = "该资料请慎重填写, 一旦确认后则无法修改"
                        this.$refs.errorMsg.style.cssText = "display: block";
                        this.$refs.realName.disabled = false;
                        this.$refs.idCard.disabled = false;
                        this.$refs.btnSuccess.disabled = false;
                    }
                }else{
                    this.$refs.errorMsg.children[0].innerHTML = "数据库异常"
                    this.$refs.errorMsg.style.cssText = "display: block";
                }
            })
        },

        // 设置实名
        setRealName: function(){
            let headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }

            // 请求体
            let data = {
                'real_name': this.realName,
                'id_card': this.idCard,
            }
            // 转json
            let jsonData = JSON.stringify(data);

            if(!this.req.test(this.idCard)){
                this.$refs.errorMsg.children[0].innerHTML = "身份证号码格式不正确, 请重新填写"
                this.$refs.errorMsg.style.cssText = "display: block";
                return false;
            }

            // 发送请求
            this.$http.post('/api/1.0/user/set-real-name', jsonData, {headers: headers}).then(function(res){
                if (res.data.errcode == "4101") {
                    location.href = "/login.html";
                }else{
                    this.$refs.errorMsg.children[0].innerHTML = res.body.errmsg
                    this.$refs.errorMsg.style.cssText = "display: block";
                    // 如果设置成功, 1.5秒后跳转到个人主页
                    if(res.data.errcode == "0"){
                        setTimeout(function(){
                            location.href = "/my.html";
                        }, 1500);
                    }
                }
            });
            return false;
        },
    },
    mounted: function(){
        // 页面加载获取信息
        this.getRealName()
    }
})

