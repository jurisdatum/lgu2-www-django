// legislation.gov.uk v4 js

// detect reducedMotion preference
	const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

// set default timeout intervals
	var animateInterval = 0

	$(document).ready(function() {
	// to undo hiding of functionality unavailable to user agents that do not have JS enabled
		$('.initialise').each(function() {
			if($(this).attr('hidden')) {
				$(this).removeAttr('hidden')
			}
			else {
				$(this).prop('hidden',true)
			}
			$(this).removeClass('initialise')
		})

	// if a table of contents
		if($('.legislation .toc-detail').length != 0) {
			$('.toc-detail li .extent').each(function() {
				$(this).addClass('hidden')
			})
		}

	// hide search on small header
		if ($(window).width() > 1023) {
			setTimeout(function(){
				$('.hdr-search details').prop('open',true)
			},10)
		}
		else {
			setTimeout(function(){
				$('.hdr-search details').removeAttr('open')
			},10)
		}
		
	// show menu on large header
		if ($(window).width() > 767) {
			setTimeout(function(){
				$('.hdr-menu details').prop('open',true)
			},10)
		}
		else {
			setTimeout(function(){
				$('.hdr-menu details').removeAttr('open')
			},10)
		}

	// light/dark mode
		$('.mode button').on('click', function() {
			var theButtonId = $(this).attr('id')
			toggleMode(theButtonId)
		})
		if(localStorage.getItem('colour-scheme')) {
			var mode = localStorage.getItem('colour-scheme')
		}
		else {
			mode = ''			
		}
		toggleMode(mode)

	// If a search results page
		if($('.search-results').length != 0) {
			if ($(window).width() < 1024 && $('.search-filters > details').attr('open')) {
				$('.search-filters > details').removeAttr('open')
			}
			else if ($(window).width() > 1023 && !$('.search-filters details').attr('open')) {
				$('.search-filters > details').prop('open',true);
			}
			if(!$('.filter-subject > details ul li:first-of-type').is('[aria-current]')) {
				$('.filter-subject > details').prop('open',true)
			}

			var theTitle = getUrlVars()["title"];
			var theYear = getUrlVars()["year"];
			var theNumber = getUrlVars()["number"];
			var theType = getUrlVars()["type"];
			if(typeof theType != 'undefined') {
				theType = theType.replace("#", "");
			}

		// Remove 'space' and '+' characters
			if(typeof theTitle != 'undefined')
			{
				theTitle = theTitle.replace(/\+/g, " ");
				theTitle = theTitle.replace(/%20/g," ");
				theTitle = theTitle.replace(/%28/g,"(");
				theTitle = theTitle.replace(/%29/g,")");
			}

		// If the 'year' parameter is empty, get year from the href
			if(typeof theYear == 'undefined')
			{
			// If the 'title' parameter is empty...
				if(typeof theTitle == 'undefined')
				{
					var testYear = this.location.href.substring(this.location.href.lastIndexOf('/') + 1);
				}
			// If the 'title' parameter is not empty...
				else
				{
					testYear = this.location.href.substring(this.location.href.lastIndexOf('/') + 1,this.location.href.indexOf('?'));
				}
				if($.isNumeric(testYear) == true)
				{
					theYear = testYear;
				}
			}

		// If the 'type' parameter is empty, specify default
			if(typeof theType == 'undefined')
			{
				theType = 'all';
			}

		// Set 'title', 'year' and 'number' inputs
			$('input#title').val(theTitle);
			$('input#year').val(theYear);
			$('input#number').val(theNumber);

		// If the 'type' parameter exists in the 'type' select, set it as the selected option
			if(theType == 'primary+secondary' || theType == 'primary%2Bsecondary' || theType == '')
			{
				$('select#type').val('primary+secondary');
			}
			else
			{
				var existsInSelect = 0 != $('select#type option[value='+theType+']').length;
				if(existsInSelect === true)
				{
					$('select#type').val(theType);
				}
			}
		// Get the long 'type' name from the select
			$('.long-type').text(getLongType);
		}

	// If not a search results page, hide search skip links
		else {
			$('header .skip-links li:not(:first-of-type)').remove()			
		}
		
		// if there is a left-hand nav, set up the link ids
		if($('.in-page-nav ol').length != 0) {
			$('.in-page-nav ol').children('li:first').children('a').attr('aria-current','page')
			$('.in-page-nav ol li:not(#main-content-h)').each(function() {
				var getHref = $(this).children('a').attr('href').replace("#", "")
				$(this).children('a').attr('id','lnk'+getHref)
			})
		}
			
	// if timeline exists
		if($('.timeline').length != 0) {
			if($('.timeline summary[disabled]').length != 0) {
				$('.timeline summary[disabled]').each(function() {
					$(this).attr('onclick','return false')
				})
			}

		// if timeline is open on page load, set scrollbar
			if($('.timeline details').is('[open]'))
			{
				setTimeout(function(){
					openTimeline()
				},1)
			}

		// timeline controls
			$('.timeline summary').on('click', function() {
				if ($(window).width() > 1023) {
					openTimeline()
					if($('.timeline details').is('[open]'))
					{
						setTimeout(function(){
							$('.timeline details').removeClass('scrollable')
						},1)
					}
				}
			})

		// selecting a version from the timeline
			$('.versions li a').on('click', function() {
				$('.timeline summary .point-in-time').remove()
				$('.versions li .point-in-time').remove()
				loadVersion(this)
			})

		// timeline scrollbar controls
			var down = false

			$('.timeline ol').scroll(function() {
				var scrollbarwidth = $('.scrollbar').width()
				var liwidth = $('.timeline ol').children('li:not(:first-of-type, :last-of-type, :has(.point-in-time)):first').width()
				var liOriginalWidth = $('.timeline ol').children('li:first-of-type').width()
				var liOriginalMargin = Number($('.timeline ol').children('li:first-of-type').css("margin-right").replace("px", ""))
				var noOfPiTs = ($('.timeline ol').children('li:not(:first-of-type, :last-of-type):has(.point-in-time)').length)
				var addForPiT = $('.timeline ol').children('li:not(:first-of-type, :last-of-type):has(.point-in-time)').outerWidth() - liwidth
				var olwidth = liOriginalWidth + liOriginalMargin + ($('.timeline ol').children('li').length - 2) * liwidth - scrollbarwidth + (addForPiT * noOfPiTs)
				var scrollx = $('.timeline ol').scrollLeft()
				var dragwidth = $('.drag').width()
				var dragstripwidth = $('.drag-strip').width()
				var thefactor = ((dragstripwidth - dragwidth) / olwidth)

				if(!down) {
					$('.drag').css('left',scrollx * thefactor)
				}

				if(scrollx >= olwidth) {
					$('.right').prop('disabled',true)
				}
				else {
					$('.right').removeAttr('disabled')
				}

				if(scrollx == 0) {
					$('.left').prop('disabled',true)
				}
				else {
					$('.left').removeAttr('disabled')
				}
			})

			$('.right').on('click', function() {
				var scrollbarwidth = $('.scrollbar').width()
				var liwidth = $('.timeline ol').children('li:not(:first-of-type, :last-of-type, :has(.point-in-time)):first').width()
				var scrollx = $('.timeline ol').scrollLeft()

				if (reducedMotion && !reducedMotion.matches) {
					animateInterval = 400
				}
				$('.timeline ol').animate({scrollLeft: scrollx + scrollbarwidth - liwidth}, animateInterval)
			})

			$('.left').on('click', function() {
				var scrollbarwidth = $('.scrollbar').width()
				var liwidth = $('.timeline ol').children('li:not(:first-of-type, :last-of-type, :has(.point-in-time)):first').width()
				var scrollx = $('.timeline ol').scrollLeft()

				if (reducedMotion && !reducedMotion.matches) {
					animateInterval = 400
				}
				$('.timeline ol').animate({scrollLeft: scrollx - scrollbarwidth + liwidth}, animateInterval)
			})

			$(function() {
				$('.drag').draggable({containment: '.drag-strip'})
			})

			$('.drag').on('drag', function() {
				down = true
				var scrollbarwidth = $('.scrollbar').width()
				var liwidth = $('.timeline ol').children('li:not(:first-of-type, :last-of-type, :has(.point-in-time)):first').width()
				var liOriginalWidth = $('.timeline ol').children('li:first-of-type').width()
				var liOriginalMargin = Number($('.timeline ol').children('li:first-of-type').css("margin-right").replace("px", ""))
				var noOfPiTs = ($('.timeline ol').children('li:not(:first-of-type, :last-of-type):has(.point-in-time)').length)
				var addForPiT = $('.timeline ol').children('li:not(:first-of-type, :last-of-type):has(.point-in-time)').outerWidth() - liwidth
				var olwidth = liOriginalWidth + liOriginalMargin + ($('.timeline ol').children('li').length - 2) * liwidth - scrollbarwidth + (addForPiT * noOfPiTs)
				var dragwidth = $('.drag').width()
				var dragstripwidth = $('.drag-strip').width()
				var thefactor = ((dragstripwidth - dragwidth) / olwidth)
				var dragleft = $('.drag').css('left').replace("px", "")

				$('.timeline ol').scrollLeft(dragleft / thefactor)
			})

			$('.drag').on('dragstop', function() {
				down = false
			})

		// open timeline if historical version is selected 
			if($(window).width() > 1023 && (!$('li:last-of-type').is('[aria-current]')))
			{
				setTimeout(function() { 
					$('.timeline details').prop('open',true)
					openTimeline()
				},150)
			}
		}
		
	// if a table of contents
		if($('.legislation .toc-detail').length != 0) {
			$('#toc').on('click', function() {
				expandToc($(this))
			})
			$('.legislation-content aside .extent button').on('click', function() {
				tocExtent($(this))
			})
		}
		
	// if there is legislation text
		if($('.legislation-text').length != 0 || $('.toc-detail').length != 0) {
		// set up markers
			$('.legislation-text li, .toc-detail li').each(function() {
				if(!$(this).attr('data-level') && $(this).parent().prop('tagName').toLowerCase() == 'ol') {
					if($(this).children(':header').eq(0).children('.prefix').length == 0){
						$(this).children(':header').eq(0).prepend($('<span class="prefix"></span>'))
					}
					if($(this).attr('value')) {
						var index = $(this).attr('value')
					}
					else if($(this).index() === 0) {
						index = 1
					}
					else
					{
						index = parseFloat($(this).prev().attr('value')) + 1
					}

					$(this).attr('value',index)

					if($(this).parent().attr('type') == 'a') {
						index = String.fromCharCode(64 + parseInt(index)).toLowerCase()
					}
					else if($(this).parent().attr('type') == 'i') {
						index = romanise(index).toLowerCase()
					}

					if($('.parenthesis').length != 0) {
						var indexPrefix = "("
						var indexSuffix = ")"
					}
					else {
						indexPrefix = ""
						indexSuffix = "."
					}
					
					if($('.toc-detail').length != 0) {
							if($(this).attr('type') != 'none') {
								if($(this).children('a .prefix').length == 0){
									$(this).children('a').prepend($('<span class="prefix"><span class="marker">' + indexPrefix + index + indexSuffix + ' </span></span>'))
								}
								else if($(this).children('.prefix').length == 0){
									$(this).prepend($('<span class="prefix"><span class="marker">' + indexPrefix + index + indexSuffix + ' </span></span>'))
								}
							}
					}
					else {
							if($(this).attr('type') != 'none') {
								if($(this).children('.prefix').length == 0){
									$(this).prepend($('<span class="prefix"><span class="marker">' + indexPrefix + index + indexSuffix + ' </span></span>'))
								}
								else if($(this).children('.prefix').length == 0){
									$(this).prepend($('<span class="prefix"><span class="marker">' + indexPrefix + index + indexSuffix + ' </span></span>'))
								}
							}
					}
					
				}
			})
		}
		
		
	// if there is a status panel
		if($('.status-panel').length != 0) {
			$('.status-panel button').on('click', function() {
				pinStatusPanel()
			})

			if(localStorage.getItem('statusPanel')) {
				var pinStatus = localStorage.getItem('statusPanel')
				if(pinStatus == 'pinned') {
					$('.status-panel').addClass('pinned')
					$('.status-panel button span').text('Unpin this panel')
				}
			}
			$('.status-panel summary').on('click', function() {
				if($('.status-panel details').is('[open]')) {
					hideStatusPanel()
				}
				else {
					showStatusPanel()
				}
			})
			
			$('.legislation-content > aside > div.not-up-to-date button').on('click', function() {
				if($('.status-panel details').is('[open]')) {
					$('.status-panel details').removeAttr('open')
					hideStatusPanel()
				}
				else {
					$('.status-panel details').prop('open',true)
					showStatusPanel()
				}
			})
		}
		

	// escape key functions
		$(document).keydown(function(e) {
			if(e.keyCode == 27) {
				if($(window).width() < 768 && $('.hdr-menu details').is('[open]'))
				{
					$('.hdr-menu details').removeAttr('open')
				}
				if($(window).width() < 1023 && $('.timeline details').is('[open]'))
				{
					$('.timeline details').removeAttr('open')
				}
				else if($(window).width() < 1023 && $('.hdr-search details').is('[open]'))
				{
					$('.hdr-search details').removeAttr('open')
				}
				if($(window).width() < 1023 && $('.search-filters > details').is('[open]'))
				{
					$('.search-filters > details').removeAttr('open')
				}
			}
		})

	// on scroll
		$(window).scroll(function() {
		// if there is a left-hand nav, set the current page attribute
			if($('.in-page-nav ol').length != 0 && $(window).width() > 1023) {
				setDynamicLeftHandNav()
			}
			
		// if status panel is pinned
			if($('.status-panel.pinned').length != 0) {
				if($(window).scrollTop() >= ($('.legislation-content > div').offset().top)) {
					setTimeout(function() {
						$('.status-panel').addClass('stuck')
					},10)
				}
				else {
					setTimeout(function() {
						$('.status-panel').removeClass('stuck')
					},10)
				}
			}
		})
		
		
	// on window resize
		$(window).resize(function() {
		// hide search on small header
			if ($(window).width() < 1024 && $('.hdr-search details').attr('open')) {
				$('.hdr-search details').removeAttr('open')
			}
			else if ($(window).width() > 1023 && !$('.hdr-search details').attr('open')) {
				$('.hdr-search details').prop('open',true)
			}
			
		// show menu on large header
			if ($(window).width() < 768 && $('.hdr-menu details').attr('open')) {
				$('.hdr-menu details').removeAttr('open')
			}
			else if ($(window).width() > 767 && !$('.hdr-menu details').attr('open')) {
				$('.hdr-menu details').prop('open',true)
			}
			
		// show search filters on higher breakpoints
			if($('.search-filters').length != 0) {
				if ($(window).width() < 1024 && $('.search-filters > details').attr('open')) {
					$('.search-filters > details').removeAttr('open')
				}
				else if ($(window).width() > 1023 && !$('.search-filters > details').attr('open')) {
					$('.search-filters > details').prop('open',true)
				}
			}
			
		// remove dynamic left-hand nav on lower breakpoints and retrigger on higher breakpoints
			if($('.in-page-nav ol').length != 0 && $(window).width() < 1024) {
				$('.in-page-nav a').removeAttr('aria-current','page')
				$('.in-page-nav ol').css('top','')
				$('.in-page-nav ol').css('bottom','')				
			}
			else if($('.in-page-nav ol').length != 0) {
				if($(window).scrollTop() < $('main article h2:first-of-type:not(nav h2)').offset().top) {
					setDynamicLeftHandNav()
				}
			}		
		})
	})

	function getUrlVars() {
		var vars = [], hash;
		var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
		for(var i = 0; i < hashes.length; i++)
		{
			hash = hashes[i].split('=');
			vars.push(hash[0]);
			vars[hash[0]] = hash[1];
		}
		return vars;
	}

	function getLongType() {
		var theTypeLong = $("select#type option:selected").text();
		return theTypeLong;
	}

	function setDynamicLeftHandNav() {
		if($(window).scrollTop() >= $('.in-page-nav ol').closest('article').offset().top && $(window).scrollTop() > ($('aside').offset().top) - $('.in-page-nav ol').outerHeight()) {
			$('.in-page-nav ol').css('top','')
			$('.in-page-nav ol').css('bottom',$('.in-page-nav ol').closest('article').css('bottom'))
		}
		else if($(window).scrollTop() >= $('.in-page-nav ol').closest('article').offset().top && $('.in-page-nav ol').css('bottom').replace("px", "") < $('aside').offset().top) {
			$('.in-page-nav ol').css('top',$(window).scrollTop() - $('.in-page-nav ol').closest('article').offset().top)
			$('.in-page-nav ol').css('bottom','')
		}
		else {
			$('.in-page-nav ol').css('top','')
			$('.in-page-nav ol').css('bottom','')
		}

		$('main article h2:not(nav h2)').each(function() {
			if($(window).scrollTop() >= $(this).offset().top - 1) {
				var subHeadId = $(this).attr("id")
				var subHeadNo = 'lnk'+ subHeadId
				$('.in-page-nav a').removeAttr('aria-current','page')
				$('.in-page-nav #' + subHeadNo).attr('aria-current','page')
			}
		})

		if($(window).scrollTop() < $('main article h2:first-of-type:not(nav h2)').offset().top) {
			$('.in-page-nav a').removeAttr('aria-current','page')
			$('.in-page-nav li:first-of-type a').attr('aria-current','page')
		}
	}

	function toggleMode(mode) {
		$('.mode button').removeClass('selected')
		if(mode == 'system' || mode == '') {
			localStorage.removeItem('colour-scheme')
			$('#system').addClass('selected')
		}
		else {
			localStorage.setItem('colour-scheme', mode)
			$('#' + mode).addClass('selected')
		}

		if((mode == 'system' || mode == '') && localStorage.getItem('colour-scheme') != '') {
			const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
			if(userPrefersDark) {
				document.documentElement.setAttribute('colour-scheme', 'dark')
			}
			else {
				document.documentElement.setAttribute('colour-scheme', 'light')
			}
			window.matchMedia('(prefers-color-scheme: dark)').addListener(({ matches }) =>
			{
				if((mode == 'system' || mode == '') && matches) {
				document.documentElement.setAttribute('colour-scheme', 'dark')
				} else if(mode == 'system' || mode == '') {
				document.documentElement.setAttribute('colour-scheme', 'light')
				}
			})
		}
		else if (localStorage.getItem('colour-scheme') != '') {
			document.documentElement.setAttribute('colour-scheme', mode)
		}
	}

	function openTimeline() {
		setTimeout(function() { 
			if($(window).width() > 1023) {
				var olWidth = $('.timeline ol').width()
				var olScrollwidth = $('.timeline ol').get(0).scrollWidth
				if(olScrollwidth > olWidth)
				{
					$('.timeline details').addClass('scrollable')
				}
			}
			$('.versions li').each(function() {
				var attr = $(this).attr('aria-current')
				if (typeof attr !== 'undefined' && attr !== false){
					loadVersion($(this).children('a'),'noanim')
				}
			})
		},1)
	}

	function loadVersion(version,anim) {
		animateInterval = 0
		version = $(version).parent()

		$('.versions li').each(function() {
			$(this).removeAttr('aria-current')
			$('.versions li a .prefix').remove()

		})
		$(version).attr('aria-current','page')
		$(version).find('.version').prepend($('<span class="prefix">You are viewing </span>'))
		
		$('.timeline summary .title').text($(version).find('.title').text().toLowerCase())
		$('.timeline summary .date').text($(version).find('.date').contents().first().text())
		$('.timeline summary .date').append($('<span>' + ($(version).find('.date span').text()) + '</span>'))
		
		var scrollbarwidth = $('.scrollbar').width()
		var liwidth = $('.timeline ol').children('li:not(:first-of-type, :last-of-type, :has(.point-in-time)):first').width()
		var noOfPiTs = ($('.timeline ol').children('li:not(:first-of-type, :last-of-type):has(.point-in-time)').length)
		var addForPiT = $('.timeline ol').children('li:not(:first-of-type, :last-of-type):has(.point-in-time)').outerWidth() - liwidth
		var index = $(version).index()

		if (reducedMotion && !reducedMotion.matches && anim != 'noanim') {
			animateInterval = 400
		}
		
		setTimeout(function(){
			$('.timeline ol').animate({scrollLeft: ((index * liwidth) + (addForPiT * noOfPiTs) + (liwidth / 2) - (scrollbarwidth * 0.5))}, animateInterval)
		},1)

		if($(window).width() < 1023)
		{
			$('.timeline details').removeAttr('open')
		}
	}

	function romanise(num) {
		if (isNaN(num))
			return NaN
		var digits = String(+num).split(''),
			key = ['','C','CC','CCC','CD','D','DC','DCC','DCCC','CM',
					'','X','XX','XXX','XL','L','LX','LXX','LXXX','XC',
					'','I','II','III','IV','V','VI','VII','VIII','IX'],
			roman = '',
			i = 3
		while (i--)
			roman = (key[+digits.pop() + (i * 10)] || '') + roman
		return Array(+digits.join('') + 1).join('M') + roman
	}

	function expandToc(element) {
		if($('#toc.expanded').length != 0) {
			$(element).removeClass('expanded')
			$(element).text('Expand table of contents')
			$('.toc-detail details').each(function() {
				$(this).removeAttr('open')
			})
		}
		else {
			$(element).addClass('expanded')
			$(element).text('Collapse table of contents')
			$('.toc-detail details').each(function() {
				$(this).prop('open',true)
			})
		}
	}

	function tocExtent(element) {
		if($('.extent button.expanded').length != 0) {
			$(element).removeClass('expanded')
			$(element).text('Show geographical extent')
			$('.toc-detail li .extent').each(function() {
				$(this).addClass('hidden')
			})
		}
		else {
			$(element).addClass('expanded')
			$(element).text('Hide geographical extent')
			$('.toc-detail li .extent').each(function() {
				$(this).removeClass('hidden')
			})
		}
	}

	function pinStatusPanel() {
		if($('.status-panel.pinned').length != 0) {
			$('.status-panel').removeClass('pinned')
			$('.status-panel').removeClass('stuck')
			$('.status-panel button span').text('Pin this panel')
			localStorage.removeItem('statusPanel')
		}
		else {
			$('.status-panel').addClass('pinned')
			$('.status-panel button span').text('Unpin this panel')
			localStorage.setItem('statusPanel', 'pinned')
		}
	}

	function showStatusPanel() {
		$('.legislation-content > aside > div.not-up-to-date button').text('Hide detail of these changes')
		$('.legislation-content > aside > div.not-up-to-date button').attr('aria-expanded',true)
		$('.status-panel summary').text('Hide detail of these changes')
	}

	function hideStatusPanel() {
		$('.status-panel summary').text('See what these changes are')
		$('.legislation-content > aside > div.not-up-to-date button').text('See what these changes are')
		$('.legislation-content > aside > div.not-up-to-date button').attr('aria-expanded',false)
	}
