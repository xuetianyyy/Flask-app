new Vue({
    el: "#v-container",
    data: {
        // 轮播用
        sliderItems: [],
        sliderItemslength: 1,
        // 存储房屋详情, 根据实际数据, 定义初始类型
        houseDetails: {},
        // 存储访客id
        call_user_id: '',
        // 存储来路
        refer_url: '',
        // 房屋设施
        facilities: [
            {id: 1,  name: '无线网络', clsName: 'wirelessnetwork-ico'},
            {id: 2,  name: '热水淋浴', clsName: 'shower-ico'},
            {id: 3,  name: '空调', clsName: 'aircondition-ico'},
            {id: 4,  name: '暖气', clsName: 'heater-ico'},
            {id: 5,  name: '允许吸烟', clsName: 'smoke-ico'},
            {id: 6,  name: '饮水设备', clsName: 'drinking-ico'},
            {id: 7,  name: '牙具', clsName: 'brush-ico'},
            {id: 8,  name: '香皂', clsName: 'soap-ico'},
            {id: 9,  name: '拖鞋', clsName: 'slippers-ico'},
            {id: 10, name: '手纸', clsName: 'toiletpaper-ico'},
            {id: 11, name: '毛巾', clsName: 'towel-ico'},
            {id: 12, name: '沐浴露、洗发露', clsName: 'toiletries-ico'},
            {id: 13, name: '冰箱', clsName: 'icebox-ico'},
            {id: 14, name: '洗衣机', clsName: 'washer-ico'},
            {id: 15, name: '电梯', clsName: 'elevator-ico'},
            {id: 16, name: '允许做饭', clsName: 'iscook-ico'},
            {id: 17, name: '允许带宠物', clsName: 'pet-ico'},
            {id: 18, name: '允许聚会', clsName: 'meet-ico'},
            {id: 19, name: '门禁系统', clsName: 'accesssys-ico'},
            {id: 20, name: '停车位', clsName: 'parkingspace-ico'},
            {id: 21, name: '有线网络', clsName: 'wirednetwork-ico'},
            {id: 22, name: '电视', clsName: 'tv-ico'},
            {id: 23, name: '浴缸', clsName: 'hotbathtub-ico'},
        ],
    },
    methods: {
        // 解析提取url中的查询字符串参数
        decodeQuery: function() {
            var search = decodeURI(document.location.search);
            return search.replace(/(^\?)/, '').split('&').reduce(function(result, item) {
                values = item.split('=');
                result[values[0]] = values[1];
                return result;
            }, {});
        },

        // 获取房屋详情信息
        getHouseDetails: function() {
            house_id = this.decodeQuery().house_id;
            this.$http.get('/api/1.0/house/details?house_id=' + house_id).then(function(res) {
                if (res.body.errcode == "0") {
                    this.houseDetails = res.body.data;
                    this.call_user_id = res.body.call_user_id;
                } else {
                    alert(res.body.errmsg);
                }
            })
            // return [];
        },

        // 获取页面路径来源
        getReferPath: function(isAll) {
            // isAll为bool值, 确定是否获取整个域名, 默认不传, 则设为false将只截取域名后面的路径包括参数
            isAll = isAll ? isAll : false;
            refer_url = document.referrer;
            path = refer_url.replace(/((http:|https:)\/\/|\d)[^\/]*/, "");
            if(isAll) path = refer_url;
            if(!path) path = '/';
            // 返回截取后的路径, 或完整URL
            return path
        },

         // 自动设置轮播窗口的高度
        setSliderHeigt: function() {
            this.$refs.swiperContainer.style.height = this.$refs.swiperContainer.offsetWidth * 0.8 + 'px';
        },

        // 设置轮播
        setSlider: function(){
            let xtSliderLength = this.$refs.swiperContainer.children.length;
            if(this.sliderItemslength >= xtSliderLength){
                this.sliderItemslength = 0;
            }
            let self = this;
            Array.from(self.$refs.swiperContainer.children).forEach(function (item, index) {
                if(index != self.sliderItemslength){
                    item.style.cssText = "right: -100%; display: none;";
                    item.style.right = '-100%';
                }else{
                    item.style.cssText = "right: 0; display: block;";
                }
            });
            this.sliderItemslength += 1;
        }
    },
    created: function() {
        this.getHouseDetails();
        this.refer_url = this.getReferPath();
    },
    mounted: function(){
        this.setSliderHeigt();
        window.addEventListener('resize', this.setSliderHeigt);
        let self = this;
        setInterval(function(){
            self.setSlider()
        }, 3000);
    },
    updated: function(){
        // 初始化显示轮播
        this.$refs.swiperContainer.children[0].style.cssText = "right: 0; display: block;";
    }
})
// data:
// acreage: 80
// address: "番禺大道南60号"
// beds: "双人床1.8*2.0m"
// capacity: 2
// comments: []
// deposit: 10000
// facilities: (10) [1, 2, 3, 4, 7, 10, 11, 12, 14, 15]
// hid: 18
// img_urls: ["http://image.weidong168.com/FsHyv4WUHKUCpuIRftvwSO_FJWOG"]
// max_days: 0
// min_days: 1
// price: 68000
// room_count: 1
// title: "最新发布"
// unit: "一室一厅一卫"
// user_avatar: "http://image.weidong168.com/Fo3fmBPIAwGsu2K576FgdJgfIvv_"
// user_id: 2
// user_name: "雪天"

// function hrefBack() {
//     history.go(-1);
// }

// // 解析提取url中的查询字符串参数
// function decodeQuery(){
//     var search = decodeURI(document.location.search);
//     return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
//         values = item.split('=');
//         result[values[0]] = values[1];
//         return result;
//     }, {});
// }

// $(document).ready(function(){
//     // 获取详情页面要展示的房屋编号
//     var queryData = decodeQuery();
//     var houseId = queryData["id"];

//     // 获取该房屋的详细信息
//     $.get("/api/v1.0/houses/" + houseId, function(resp){
//         if ("0" == resp.errno) {
//             $(".swiper-container").html(template("house-image-tmpl", {img_urls:resp.data.house.img_urls, price:resp.data.house.price}));
//             $(".detail-con").html(template("house-detail-tmpl", {house:resp.data.house}));

//             // resp.user_id为访问页面用户,resp.data.user_id为房东
//             if (resp.data.user_id != resp.data.house.user_id) {
//                 $(".book-house").attr("href", "/booking.html?hid="+resp.data.house.hid);
//                 $(".book-house").show();
//             }
//             var mySwiper = new Swiper ('.swiper-container', {
//                 loop: true,
//                 autoplay: 2000,
//                 autoplayDisableOnInteraction: false,
//                 pagination: '.swiper-pagination',
//                 paginationType: 'fraction'
//             });
//         }
//     })
// })
