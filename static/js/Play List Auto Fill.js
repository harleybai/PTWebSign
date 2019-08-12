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
		let bgm_link = $('input#f_bgm').val().trim();
		requestHTML(bgm_link, function (res) {
			let page = $(res.responseText.match(/<body[^>]*?>([\S\s]+)<\/body>/)[1].replace(/<script(\s|>)[\S\s]+?<\/script>/g, ''));

			// 标题
			let title = page.find("h1.nameSingle>a").text();
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
	});

})();