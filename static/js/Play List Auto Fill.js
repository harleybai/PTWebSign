// ==UserScript==
// @name        Play List Auto Fill
// @namespace   playlistautofill
// @description Play List 自动填写信息
// @author      harleybai
// @grant       unsafeWindow
// @grant       GM_xmlhttpRequest
// @include     http://127.0.0.1:8080/playlist*
// @version     20260613
// ==/UserScript==

/* global $ */
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

	function fillInfo(data) {
		console.log("fillInfo: ", data)
		if (data?.pic && !$('input#f_pic').val()) $('input#f_pic').val(data.pic);
		if (data?.progress) {
			const pNow = $('input#f_progress').val().trim() == '' ? 0 : parseInt($('input#f_progress').val().trim());
			$('input#f_progress').val(pNow + '/' + data.progress);
		}
		if (data?.title) $('input#f_title').val(data.title);
		if (data?.date) $('input#f_date').val(data.date);
		if (data?.time) $('input#f_time').val(data.time);
		if (data?.week) {
			$("#d_week input:checkbox").each(function () {
				$(this).prop("checked", false);
				if (data.week.includes($(this).val()) || data.week.includes($(this).closest('label').text())) {
					$(this).prop("checked", true);
				}
			});
		}
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
				let weekday = "";

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
							if (key == m[1]) { isPush = true; }
							if (isPush) { weekdayChecked.push(weekToEnglish[key]); }
							if (key == m[3]) { isPush = false; }
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
				fillInfo({
					'pic': img,
					'title': title,
					'progress': progress_total,
					'date': '',
					'week': weekday ? [weekday] : [],
					'time': time,
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

				fillInfo({
					'pic': img,
					'title': title,
					'progress': progress_total,
					'date': '',
					'week': weekday ? [weekday] : [],
					'time': '',
				});
			}, function (res) {
				console.log('查询影片的BGM信息失败...', res);
			});
		} else if (cat == '2') {
			requestHTML($('input#f_douban').val().trim(), function (res) {
				const page = $(res.responseText.match(/<body[^>]*?>([\S\s]+)<\/body>/)[1].replace(/<script(\s|>)[\S\s]+?<\/script>/g, ''));

				let title = page.find('h1>span:first').text().trim().replace(/[\w\d-\s:,]*$/, '');// 标题
				let img = page.find("div#mainpic img").attr("src");// 海报
				let date = page.find("div#info span[property='v:initialReleaseDate']").text().match(/\d+-\d+-\d+/);// 日期
				let progress_total = '';// 总集数
				let akaText = ''; // 别名
				page.find('.pl').each(function () {
					const label = $(this).text().trim();
					const textNode = this.nextSibling;
					if (label === '集数:') progress_total = parseInt(textNode.textContent.trim()) || 0;
					if (label === '又名:') akaText = textNode.textContent.trim();
				});
				fillInfo({
					'pic': img.match(/^http/) ? img : '',
					'title': title,
					'progress': progress_total,
					'date': date ? date[0] : '',
					'week': [],
					'time': '',
				});
			}, function (res) {
				console.log('查询影片的豆瓣信息失败...', res);
			});
		}

	});

})();