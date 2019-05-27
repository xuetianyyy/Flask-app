new Vue({
    el: "#v-container",
    data: {
        reg: /^1[3456789]\d{9}$/, // 验证手机的正则
        mobile: '',
        password: '',
    },
    methods: {
        // 获取cookie值
        getCookie: function(key_name) {
            var r = document.cookie.match("\\b" + key_name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 表单输入框验证
        isInputData: function(event){
            if (event.target.name == 'mobile') {
                // 手机号验证
                if (this.reg.test(this.mobile)) {
                    this.$refs.mobileErr.style.cssText = "display:none;";
                }else{
                    this.$refs.mobileErr.children[0].innerHTML = "请输入正确的手机号";
                    this.$refs.mobileErr.style.cssText = "display:block;";
                }
                return
            }else if(event.target.name == 'password'){
                // 密码验证
                if(this.password){
                    this.$refs.passwordErr.style.cssText = "display:none;";
                }else{
                    this.$refs.passwordErr.children[0].innerHTML = "请输入登录密码!";
                    this.$refs.passwordErr.style.cssText = "display:block;";
                }
                return
            }
        },

        // 用户登录
        userLogin: function(){
            let data = {
                mobile: this.mobile,
                password: this.password,
            }
            // 转json
            let jsonData = JSON.stringify(data);
            // 设置包头
            let headers = {
                contentType: "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }

            // 发送请求
            this.$http.post('/api/1.0/user/login', jsonData, {headers: headers}).then(function(result){
                if (result.data.errcode == "0"){
                    // 登录成功，跳转到主页
                    location.href = "/";
                }else{
                    // 其它错误显示在psswordErr中
                    this.$refs.passwordErr.children[0].innerHTML = result.data.errmsg;
                    this.$refs.passwordErr.style.cssText = "display:block;";
                }
            })
            return false;
        },
    },

    created() {
        // console.log(this);
    },
})
