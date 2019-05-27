new Vue({
    el: "#v-container",
    data: {
        imageFiles: '',
        username: '',
    },
    methods: {
        // 获取cookie
        getCookie: function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 获取图片资源, 并上传
        getFiles: function() {
            // 获取到的files对象示例: FileList {0: File, length: 1}
            this.imageFiles = this.$refs.imageFile.files[0]
            // 设置请求头
            headers = {
                // 注意要设置内容类型为多媒体
                'Content-Type': 'multipart/form-data',
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            // 创建表单数据对象
            let formData = new FormData();
            formData.append('image_file', this.imageFiles);

            // 发送请求
            this.$http.post('/api/1.0/user/portrait', formData, {
                headers: headers
            }, {
                emulateJSON: true
            }).then(function(res) {
                if (res.body.errcode == "0") {
                    this.$refs.userImage.src = res.body.image_url
                } else if (res.body.errcode == "4101") {
                    location.href = "/login.html";
                } else {
                    alert(res.body.errmsg)
                }
            })
            return false;
        },

        // 设置用户名
        setUsername: function() {
            headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            // 请求体
            data = {
                'username': this.username
            }
            // 转json
            let jsonData = JSON.stringify(data);
            // 发送请求
            this.$http.post('/api/1.0/user/set-username', jsonData, {
                headers: headers
            }).then(function(res) {
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
            })
        },
    },
    mounted: function() {
        // console.log(this.$refs);
    }
})

// function showSuccessMsg() {
//     $('.popup_con').fadeIn('fast', function() {
//         setTimeout(function(){
//             $('.popup_con').fadeOut('fast',function(){});
//         },1000)
//     });
// }

// function getCookie(name) {
//     var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
//     return r ? r[1] : undefined;
// }


// $(document).ready(function () {
//     $("#form-avatar").submit(function (e) {
//         // 阻止表单的默认行为
//         e.preventDefault();
//         // 利用jquery.form.min.js提供的ajaxSubmit对表单进行异步提交
//         $(this).ajaxSubmit({
//             url: "/api/v1.0/users/avatar",
//             type: "post",
//             dataType: "json",
//             headers: {
//                 "X-CSRFToken": getCookie("csrf_token")
//             },
//             success: function (resp) {
//                 if (resp.errno == "0") {
//                     // 上传成功
//                     var avatarUrl = resp.data.avatar_url;
//                     $("#user-avatar").attr("src", avatarUrl);
//                 } else if (resp.errno == "4101") {
//                     location.href = "/login.html";
//                 } else {
//                     alert(resp.errmsg);
//                 }
//             }
//         })
//     });

//     // 在页面加载是向后端查询用户的信息
//     $.get("/api/v1.0/user", function(resp){
//         // 用户未登录
//         if ("4101" == resp.errno) {
//             location.href = "/login.html";
//         }
//         // 查询到了用户的信息
//         else if ("0" == resp.errno) {
//             $("#user-name").val(resp.data.name);
//             if (resp.data.avatar) {
//                 $("#user-avatar").attr("src", resp.data.avatar);
//             }
//         }
//     }, "json");

//      $("#form-name").submit(function(e){
//         e.preventDefault();
//         // 获取参数
//         var name = $("#user-name").val();

//         if (!name) {
//             alert("请填写用户名！");
//             return;
//         }
//         $.ajax({
//             url:"/api/v1.0/users/name",
//             type:"PUT",
//             data: JSON.stringify({name: name}),
//             contentType: "application/json",
//             dataType: "json",
//             headers:{
//                 "X-CSRFTOKEN":getCookie("csrf_token")
//             },
//             success: function (data) {
//                 if ("0" == data.errno) {
//                     $(".error-msg").hide();
//                     showSuccessMsg();
//                 } else if ("4001" == data.errno) {
//                     $(".error-msg").show();
//                 } else if ("4101" == data.errno) {
//                     location.href = "/login.html";
//                 }
//             }
//         });
//     })
// })
