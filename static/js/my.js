    var ws = null;
    var username = null;
    var img1 = null;
    var img2 = null;
    var chat_id = null;
    window.onload = function () {
        img1 = document.getElementById("xxx").innerText;
        document.getElementById('pic_recv').src = 'http://127.0.0.1:5000/get_img/' + img1;
        username = document.getElementById("username").innerText;
        create_ws(username);
    };

    // 监听电话
    function create_ws(username) {
        ws = new WebSocket("ws://127.0.0.1:9528/ws/" + username);
        ws.onmessage = function (eventMessage) {
            console.log(eventMessage.data);
            str_obj = JSON.parse(eventMessage.data);

            //创建table
            if (str_obj.status == 0|str_obj.status == 1) {
                var tb = document.getElementById('tb');
                tb.innerHTML = '';
                var b = 1;
                var ava = str_obj.avatar;
                var lock = str_obj.chating;
                $.each(str_obj.users, function (i, n) {
                    console.log(n,lock);
                    var tr = document.createElement('tr');
                    var bq = document.createElement('td');
                    if (lock.indexOf(n) >= 0) {
                        bq = `<td><button id=${i} name='btn' class="btn btn-sm btn-warning">解绑</button></td>`
                    } else {
                        bq = `<td><button id=${i} name='btn' class="btn btn-sm btn-danger" onclick="xxx('${n}')">单聊</button></td>`
                    }

                    //排除自己信息
                    if (n != username) {
                        tr.innerHTML = `
                        <td>${b}</td>
                        <td>${n}</td>
                        ${bq}
                        `;
                        b += 1;
                        tb.append(tr);
                    }
                });
            }

            //自动加载部分
            var p = document.createElement("p");
            var n = document.getElementById('count');
            n.innerText = str_obj.count;

            //更新聊天框
            if (str_obj.status == 1) {
                var from = str_obj.from_user;
                var chat = str_obj.chat;
                var img22 = str_obj.img;
                document.getElementById('friend').innerText = from;
                var media = ` <div class="media">
                        <div class="media-left">
                            <img class="media-object" style="width:70px;height: 70px;border-radius: 50%" src='http://127.0.0.1:5000/get_img/${img22}'>
                        </div>
                        <div class="media-body">
                            <h4 class="media-heading">${from}</h4>
                            <p>${chat}</p>
                        </div>
                    </div>`;
                $('#panel').append(media);
                if (img2 == null) {
                    img2 = img1;
                }
            }
        };
    }

    $('#open').click(function () {
        sendStr = {
            to_user: username,
            status: 0,
        };
        ws.send(JSON.stringify(sendStr));
    });

    function xxx(name) {
        document.getElementById('friend').innerText = name;
        $.ajax({
            url: `/get_chat/${name}/${username}`,
            success: function (res) {
                console.log(JSON.stringify(res));
                if (res['code'] == 2) {
                    console.log(res.data['img']);
                    img2 = res.data['img'];
                    chat_id = res.data['chat_id'];
                }
            }
        })
    }


    $('#send').click(function () {
        var to_user = document.getElementById("friend").innerText;
        var content = document.getElementById('content').value;

        console.log(username, to_user, content);
        var sendStr = {
            from_user: username,
            to_user: to_user,
            chat: content,
            img: img2,
            status: 1,
        };

        console.log(JSON.stringify(sendStr));
        ws.send(JSON.stringify(sendStr));

        var media = ` <div class="media">
                        <div class="media-right pull-right">
                            <img class="media-object" style="width:70px;height: 70px;border-radius: 50%" src='http://127.0.0.1:5000/get_img/${img1}'>
                        </div>
                        <div class="media-body">
                            <h4 class="media-heading text-right">${username}</h4>
                            <p class='text-right'>${content}</p>
                        </div>
                    </div>`;

        $('#panel').append(media);
        document.getElementById('content').value = "";
    })