// ==UserScript==
// @name        Play List Auto Fill
// @namespace   playlistautofill
// @description Play List 自动填写信息
// @author      harleybai
// @grant       unsafeWindow
// @grant       GM_xmlhttpRequest
// @include     http://127.0.0.1:8080/playlist*
// @version     20190812
// ==/UserScript==

(function () {

	function requestData(url, successHandle, timeoutHandle) {
		GM_xmlhttpRequest({
			method: 'GET',
			url: url,
			timeout: 5000,
			onreadystatechange: successHandle,
			ontimeout: timeoutHandle,
		});
	}

	function requestHTML(url, successHandle, timeoutHandle) {
		requestData(url, function (response) {
			if (response.readyState == 4) {
				successHandle(response);
			}
		}, function (response) {
			timeoutHandle(response);
		});
	}

	$('#bgm_auto_fill').click(function () {
		let cat = $('select#searchcat').val();
		if (cat == '0') {
			let link = $('input#f_video').val().trim();
			requestHTML(link, function (res) {
				let page = $(res.responseText.match(/<body[^>]*?>([\S\s]+)<\/body>/)[1].replace(/<script(\s|>)[\S\s]+?<\/script>/g, ''));
				// 标题
				let title = "";
				// 海报
				let img = "";
				// 放送星期
				let weekToEnglish = {
					'一': 'Monday',
					'二': 'Tuesday',
					'三': 'Wednesday',
					'四': 'Thursday',
					'五': 'Friday',
					'六': 'Saturday',
					'日': 'Sunday'
				}
				var weekdayChecked = [];
				// 更新时间
				let time = "";
				// 总集数
				let progress_total = 0;

				if (link.match(/www\.bilibili\.com/)) {
					img = page.find("#app div.common-lazy-img>img").attr("src");
					title = page.find("#app div.media-info-title>span.media-info-title-t").text();
					weekday = page.find("#app div.media-info-time>span:contains('更新')").text();
					time = weekday.match(/\d+:\d+/) ? weekday.match(/\d+:\d+/)[0] : '10:00';
				} else {
					title = page.find("h1.video_title_cn>a:first").text();
					img = page.find("div.container_inner img.figure_pic").attr("src");
					weekday = page.find("div.type_item:contains('更新时间')>span.type_txt").text().replace('点', ':00');
					time = weekday.match(/\d+:\d+/) ? weekday.match(/\d+:\d+/)[0] : '10:00';
					progress_total = parseInt(page.find("div.type_item:contains('总集数')>span.type_txt").text());
					progress_total = progress_total ? progress_total : 0;
				}
				img = img.match(/^http/) ? img : 'http:' + img;
				let m = weekday.match(/周(.)(至周(.))?/);
				if (m) {
					weekdayChecked.push(weekToEnglish[m[1]]);
					if (m[3]) {
						let isPush = false;
						for (let key in weekToEnglish) {
							if (key == m[1])
								isPush = true;
							if (isPush)
								weekdayChecked.push(weekToEnglish[key]);
							if (key == m[3])
								isPush = false;
						}
					}
				}
				m = weekday.match(/周(.)(、(.))?/);
				if (m) {
					weekdayChecked.push(weekToEnglish[m[1]]);
					if (m[3]) {
						weekdayChecked.push(weekToEnglish[m[3]]);
					}
				}

				console.log(`标题: ${title}, 海报: ${img}, 放送星期: ${weekday}, 时间: ${time}, 总集数: ${progress_total}`);
				// 填写
				$('input#f_pic').val(img);
				$('input#f_title').val(title);
				$('input#f_time').val(time);
				let progress_now = $('input#f_progress').val().trim() == '' ? 0 : parseInt($('input#f_progress').val().trim());
				$('input#f_progress').val(progress_now + '/' + progress_total);


				$("input:checkbox").each(function () {
					if (weekdayChecked.indexOf($(this).val()) >= 0) {
						$(this).prop("checked", true);
					} else if ($(this).prop("checked")) {
						$(this).prop("checked", false);
					}
				});

			}, function (res) {
				console.log('查询影片的BGM信息失败...', res);
			});
		} else if (cat == '1') {
			let link = $('input#f_bgm').val().trim();
			requestHTML(link, function (res) {
				let page = $(res.responseText.match(/<body[^>]*?>([\S\s]+)<\/body>/)[1].replace(/<script(\s|>)[\S\s]+?<\/script>/g, ''));

				// 标题
				let title = page.find("ul#infobox>li:contains('中文名')").text().trim().replace('中文名: ', '');
				// 海报
				let img = page.find("div#bangumiInfo>div>div:nth-child(1)>a>img").attr("src").replace(/cover\/[lcmsg]/, "cover/l");
				img = img.match(/^http/) ? img : 'http:' + img;
				// 放送星期
				let weekday = page.find("ul#infobox>li:contains('放送星期')").text().trim().match(/星期.$/)[0];
				// 总集数
				let progress_total = parseInt(page.find("ul.prg_list a.load-epinfo:last").text());

				console.log(`标题: ${title}, 海报: ${img}, 放送星期: ${weekday}, 总集数: ${progress_total}`);
				// 填写
				$('input#f_pic').val(img);
				$('input#f_title').val(title);
				let progress_now = $('input#f_progress').val().trim() == '' ? 0 : parseInt($('input#f_progress').val().trim());
				$('input#f_progress').val(progress_now + '/' + progress_total);

				var weekToEnglish = {
					'星期一': 'Monday',
					'星期二': 'Tuesday',
					'星期三': 'Wednesday',
					'星期四': 'Thursday',
					'星期五': 'Friday',
					'星期六': 'Saturday',
					'星期日': 'Sunday'
				}
				$("input:checkbox").each(function () {
					if ($(this).val() == weekToEnglish[weekday]) {
						$(this).prop("checked", true);
					} else if ($(this).prop("checked")) {
						$(this).prop("checked", false);
					}
				});

			}, function (res) {
				console.log('查询影片的BGM信息失败...', res);
			});
		} else if (cat == '2') {
			let link = $('input#f_douban').val().trim();
			requestHTML(link, function (res) {
				let page = $(res.responseText.match(/<body[^>]*?>([\S\s]+)<\/body>/)[1].replace(/<script(\s|>)[\S\s]+?<\/script>/g, ''));

				// 标题
				let title = page.find('h1>span:first').text().trim().replace(/[\w\d-\s:,]*$/, '');
				// 海报
				let img = page.find("div#mainpic img").attr("src");
				img = img.match(/^http/) ? img : 'http:' + img;
				// 总集数
				let progress_total = 1;
				// 日期
				let date = page.find("div#info span[property='v:initialReleaseDate']").text().match(/\d+-\d+-\d+/)[0];

				console.log(`标题: ${title}, 海报: ${img}, 总集数: ${progress_total}, 日期: ${date}`);
				// 填写
				$('input#f_pic').val(img);
				$('input#f_title').val(title);
				let progress_now = $('input#f_progress').val().trim() == '' ? 0 : parseInt($('input#f_progress').val().trim());
				$('input#f_progress').val(progress_now + '/' + progress_total);
				$('input#f_date').val(date);

			}, function (res) {
				console.log('查询影片的BGM信息失败...', res);
			});
		}

	});

})();