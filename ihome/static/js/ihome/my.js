new Vue({
    el: "#v-container",
    data: {

    },
    methods: {
        getCookie: function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 获取用户信息
        getUserMsg: function(){
            this.$http.get('/api/1.0/user/get-user-msg').then(function(res){
                if (res.data.errcode == "4101") {
                    location.href = "/login.html";
                }else{
                    this.$refs.userImage.src = res.data.image_url;
                    this.$refs.username.innerHTML = res.data.username;
                    this.$refs.mobile.innerHTML = res.data.mobile;
                }
            })
        },


        // 用户退出
        userLogout: function(){
            let headers = {
                "X-CSRFToken": this.getCookie("csrf_token")
            };
            this.$http.delete("/api/1.0/user/session", {headers: headers}).then(function(res){
                if(res.body.errcode == "0"){
                    location.href = "/";
                }
            })
        },
    },


    mounted: function() {
        // 页面加载获取用户信息
        this.getUserMsg();
    },
})
