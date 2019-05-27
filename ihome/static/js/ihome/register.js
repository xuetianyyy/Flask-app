new Vue({
    el: '#v-container',
    data: {
        // 保存图片验证码编号
        imageCodeId: "",
        is_pointer_style: {
            pointerEvents: 'auto'
        },
        reg: /^1[3456789]\d{9}$/, // 验证手机的正则
        mobile: '',     // 绑定用户输入的手机号
        imagecode: '',  // 绑定用户输入的图片验证码
        phonecode: '',  // 绑定用户输入的手机验证码
        password: '',   // 绑定用户输入的第一次的密码
        password2: '',  // 绑定用户输入的第二次的密码
    },
    methods: {
        // js读取cookie的方法
        getCookie: function(name) {
            // name为需要获取的cookie键名, 例如: 'csrf_token'
            let r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 创建一个验证码编号
        generateUUID: function() {
            let d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                let r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },

        // 形成图片验证码的后端地址， 设置到页面中，让浏览请求验证码图片
        generateImageCode: function() {
            // 1. 生成图片验证码编号
            this.imageCodeId = this.generateUUID();
            // 是指图片url
            let url = "/api/1.0/image_code/" + this.imageCodeId;
            this.$refs.img_code.src = url;
        },

        // 点击发送短信验证码后被执行的函数
        sendSMSCode: function() {
            // 设置禁用元素点击
            this.is_pointer_style.pointerEvents = 'none';

            if (!this.reg.test(this.mobile)) {
                this.$refs.mobileErr.children[0].innerHTML = "请输入正确的手机号";
                this.$refs.mobileErr.style.cssText = "display:block;";
                // 开启元素的点击功能
                this.is_pointer_style.pointerEvents = 'auto';
                return
            }
            if (!this.imagecode) {
                this.$refs.imageCodeErr.children[0].innerHTML = "请输入图片验证码!";
                this.$refs.imageCodeErr.style.cssText = "display:block;";
                // 恢复按钮点击功能
                this.is_pointer_style.pointerEvents = 'auto';
                return
            }

            // 构造向后端请求的参数
            var req_data = {
                image_code_id: this.imageCodeId, // 图片验证码的编号
                image_code: this.imagecode,      // 图片验证码的值
            };

            // 向后端发送请求
            this.$http.get("/api/1.0/sms_code/" + this.mobile, {
                params: req_data
            }).then(function(result) {
                alert(result.data.errmsg);
                if (result.data.errcode == "0") {
                    // 存储this的指向
                    let self = this
                    let num = 60;
                    // 表示发送成功
                    let timer = setInterval(function() {
                        // console.log(self);
                        if (num >= 1) {
                            // 修改倒计时文本
                            self.$refs.phonecode_a.innerHTML = num + "秒后重试";
                            num -= 1;
                        } else {
                            self.$refs.phonecode_a.innerHTML = "获取验证码";
                            self.is_pointer_style.pointerEvents = 'auto';
                            clearInterval(timer);
                        }
                    }, 1000, 60)
                } else {
                    this.is_pointer_style.pointerEvents = 'auto';
                }
            })
        },

        // 检测用户输入的离开焦点事件
        isInputData: function(event) {

            if (event.target.name == 'mobile') {
                // 手机号验证
                if (this.reg.test(this.mobile)) {
                    this.$refs.mobileErr.style.cssText = "display:none;";
                }else{
                    this.$refs.mobileErr.children[0].innerHTML = "请输入正确的手机号";
                    this.$refs.mobileErr.style.cssText = "display:block;";
                }
                return
            }else if(event.target.name == 'imagecode'){
                // 图片验证码验证
                if(this.imagecode){
                    this.$refs.imageCodeErr.style.cssText = "display:none;";
                }else{
                    this.$refs.imageCodeErr.children[0].innerHTML = "请输入图片验证码!";
                    this.$refs.imageCodeErr.style.cssText = "display:block;";
                }
                return
            }else if(event.target.name == 'phonecode'){
                // 手机验证码验证
                if(this.phonecode){
                    this.$refs.phoneCodeErr.style.cssText = "display:none;";
                }else{
                    this.$refs.phoneCodeErr.children[0].innerHTML = "请输入短信验证码!";
                    this.$refs.phoneCodeErr.style.cssText = "display:block;";
                }
                return
            }else if(event.target.name == 'password'){
                // 密码验证
                if(this.password){
                    this.$refs.passwordErr.style.cssText = "display:none;";
                }else{
                    this.$refs.passwordErr.children[0].innerHTML = "请输入注册密码!";
                    this.$refs.passwordErr.style.cssText = "display:block;";
                }
                return
            }else if(event.target.name == 'password2'){
                // 二次密码验证
                if(this.password2 && (this.password == this.password2)){
                    this.$refs.password2Err.style.cssText = "display:none;";
                    return
                }else{
                    if(!this.password2){
                        this.$refs.password2Err.children[0].innerHTML = "请再次输入密码!";
                        this.$refs.password2Err.style.cssText = "display:block;";
                    }else{
                        this.$refs.password2Err.children[0].innerHTML = "两次输入的密码不一致, 请重新输入!";
                        this.$refs.password2Err.style.cssText = "display:block;";
                    }
                }
            }
        },

        // 注册的函数
        userRegister: function() {
            console.log('注册开始');
            if(!this.mobile || !this.phonecode || !this.password || !this.password2){
                alert('请将资料填写完整!')
            }
            let data = {
                mobile: this.mobile,
                sms_code: this.phonecode,
                password: this.password,
                password2: this.password2,
            }
            // 包头
            let headers = {
                contentType: "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            // 发送json格式的数据
            let req_json = JSON.stringify(data);
            this.$http.post('/api/1.0/user/register', req_json, {headers: headers}).then(function(result){
                if (result.data.errcode == "0"){
                    // 注册成功，跳转到主页
                    location.href = "/";
                }else{
                    alert(result.data.errmsg);
                }
            })
            return false;
        },
    },

    created() {
        // console.log(this);
    },
    mounted() {
        // 初始化, 获取第一次的图片验证码
        this.generateImageCode()
    },
})
