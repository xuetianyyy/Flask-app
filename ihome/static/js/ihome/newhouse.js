new Vue({
    el: "#v-container",
    data: {
        // 存储区域的对象列表
        area_obj_arr: [],
        // 房屋信息的参数
        title: '',
        price: '',
        area_id: '',
        address: '',
        room_count: '',
        acreage: '',
        unit: '',
        capacity: '',
        beds: '',
        deposit: '',
        min_days: '',
        max_days: '',
        facility: [],  // 房屋设施复选框
        // 存储房屋id
        house_id: null,
        // 存储图片文件
        imageFiles: null,
        // 存储图片路径列表
        imageUrls: [],
    },
    methods: {
        // 获取cookie
        getCookie: function(name) {
            var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        },

        // 获取城区列表
        getMyHouse: function() {
            this.$http.get('/api/1.0/house/get-area-info').then(function(res) {
                if (res.body.errcode == "0") {
                    this.area_obj_arr = res.body.data;
                    // console.log(res.body.data);
                }
            })
        },

        // 设置房屋信息
        setHouseMsg: function() {
            headers = {
                'Content-Type': "application/json",
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            data = {
                title: this.title,
                price: this.price,
                area_id: this.area_id,
                address: this.address,
                room_count: this.room_count,
                acreage: this.acreage,
                unit: this.unit,
                capacity: this.capacity,
                beds: this.beds,
                deposit: this.deposit,
                min_days: this.min_days,
                max_days: this.max_days,
                facility: this.facility,
            }
            // 转json
            let jsonData = JSON.stringify(data);
            this.$http.post('/api/1.0/house/save-houses-info', jsonData, {headers: headers}).then(function(res){
                if(res.body.errcode == "0"){
                    // 获取房屋id
                    this.house_id = res.body.data.house_id;
                    // 隐藏房屋提交表单
                    this.$refs.formHouseInfo.style.cssText = "display:none;";
                    // 显示图片提交表单
                    this.$refs.formHouseImage.style.cssText = "display:block;";
                }else{
                    this.$refs.errorMsg.children[0].innerHTML = res.body.errmsg;
                    this.$refs.errorMsg.style.cssText = "display: block;";
                }
            })
            // console.log(data);
        },

        // 设置房屋图片
        setHouseImage: function(){
            // 获取图片文件
            this.imageFiles = this.$refs.imageFile.files[0]
            // 设置请求头
            headers = {
                'Content-Type': 'multipart/form-data',
                "X-CSRFToken": this.getCookie("csrf_token")
            }
            // 创建表单数据对象
            let formData = new FormData();
            formData.append('image_file', this.imageFiles);
            formData.append('house_id', this.house_id);

            // 发送请求, 这里也要设置发送类型为表单格式{emulateJSON: true}
            this.$http.post('/api/1.0/house/image', formData, {headers: headers}, {emulateJSON: true}).then(function(res){
                // 获取响应码
                if(res.body.errcode == "0"){
                    // 将图片路径添加到列表中
                    // console.log(res.body);
                    this.imageUrls.push(res.body.data.image_url)
                }else if(res.body.errcode == "4101"){
                    location.href = "/login.html";
                }else{
                    alert(res.body.errmsg)
                }
            })
            return false;
        },
    },

    created: function() {
        this.getMyHouse();
    },
    mounted: function() {

    },
})

// $(document).ready(function(){
//     // 向后端获取城区信息
//     $.get("/api/v1.0/areas", function (resp) {
//         if (resp.errno == "0") {
//             var areas = resp.data;
//             // for (i=0; i<areas.length; i++) {
//             //     var area = areas[i];
//             //     $("#area-id").append('<option value="'+ area.aid +'">'+ area.aname +'</option>');
//             // }

//             // 使用js模板
//             var html = template("areas-tmpl", {areas: areas})
//             $("#area-id").html(html);

//         } else {
//             alert(resp.errmsg);
//         }

//     }, "json");

//     $("#form-house-info").submit(function (e) {
//         e.preventDefault();

//         // 处理表单数据
//         var data = {};
//         $("#form-house-info").serializeArray().map(function(x) { data[x.name]=x.value });

//         // 收集设置id信息
//         var facility = [];
//         $(":checked[name=facility]").each(function(index, x){facility[index] = $(x).val()});

//         data.facility = facility;

//         // 向后端发送请求
//         $.ajax({
//             url: "/api/v1.0/houses/info",
//             type: "post",
//             contentType: "application/json",
//             data: JSON.stringify(data),
//             dataType: "json",
//             headers: {
//                 "X-CSRFToken": getCookie("csrf_token")
//             },
//             success: function (resp) {
//                 if (resp.errno == "4101") {
//                     // 用户未登录
//                     location.href = "/login.html";
//                 } else if (resp.errno == "0") {
//                     // 隐藏基本信息表单
//                     $("#form-house-info").hide();
//                     // 显示图片表单
//                     $("#form-house-image").show();
//                     // 设置图片表单中的house_id
//                     $("#house-id").val(resp.data.house_id);
//                 } else {
//                     alert(resp.errmsg);
//                 }
//             }
//         })

//     });
//     $("#form-house-image").submit(function (e) {
//         e.preventDefault();
//         $(this).ajaxSubmit({
//             url: "/api/v1.0/houses/image",
//             type: "post",
//             dataType: "json",
//             headers: {
//                 "X-CSRFToken": getCookie("csrf_token"),
//             },
//             success: function (resp) {
//                 if (resp.errno == "4101") {
//                     location.href = "/login.html";
//                 } else if (resp.errno == "0") {
//                     $(".house-image-cons").append('<img src="' + resp.data.image_url +'">');
//                 } else {
//                     alert(resp.errmsg);
//                 }
//             }
//         })
//     })

// })
