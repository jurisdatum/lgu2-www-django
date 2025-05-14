// legislation.gov.uk v4 js

// detect reducedMotion preference
	const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

// set default timeout intervals
	var animateInterval = 0

	$(document).ready(function() {
	// to undo hiding of functionality unavailable to people who do not have JS enabled
		$('.initialise').each(function() {
			if($(this).attr('hidden')) {
				$(this).removeAttr('hidden')
			}
			else {
				$(this).attr('hidden',true)
			}
			$(this).removeClass('initialise')
		})

	// hide search on small header
		if ($(window).width() > 1023) {
			setTimeout(function(){
				$('.hdr-search details').attr('open',true)
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
				$('.hdr-menu details').attr('open',true)
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
			mode = 'system'			
		}
		toggleMode(mode)

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
					$('.right').attr('disabled','disabled')
				}
				else {
					$('.right').removeAttr('disabled')
				}

				if(scrollx == 0) {
					$('.left').attr('disabled','disabled')
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
					$('.timeline details').attr('open',true)
					openTimeline()
				},150)
			}
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
			}
		})

	// on scroll
		$(window).scroll(function() {
		// if there is a left-hand nav, set the current page attribute
			if($('.in-page-nav ol').length != 0 && $(window).width() > 1023) {
				setDynamicLeftHandNav()
			}
		})

	// on window resize
		$(window).resize(function() {
		// hide search on small header
			if ($(window).width() > 1023) {
				setTimeout(function(){
					$('.hdr-search details').attr('open',true)
				},10)
			}
			
		// show menu on large header
			if ($(window).width() > 767) {
				setTimeout(function(){
					$('.hdr-menu details').attr('open',true)
				},10)
			}
			else {
				setTimeout(function(){
					$('.hdr-menu details').removeAttr('open')
				},10)
			}
			
		// remove dynamic left-hand nav on lower breakpoints
			if($('.in-page-nav ol').length != 0 && $(window).width() < 1024) {
				$('.in-page-nav a').removeAttr('aria-current','page')
				$('.in-page-nav ol').css('top','')
				$('.in-page-nav ol').css('bottom','')				
			}
			
		// and retrigger on higher breakpoints
			else if($('.in-page-nav ol').length != 0) {
				if($(window).scrollTop() < $('main section h2:first-of-type:not(nav h2)').offset().top) {
					setDynamicLeftHandNav()
				}
			}
		})
	})

	function setDynamicLeftHandNav() {
		if($(window).scrollTop() >= $('.in-page-nav ol').closest('section').offset().top && $(window).scrollTop() > ($('aside').offset().top) - $('.in-page-nav ol').outerHeight()) {
			$('.in-page-nav ol').css('top','')
			$('.in-page-nav ol').css('bottom',$('.in-page-nav ol').closest('section').css('bottom'))
		}
		else if($(window).scrollTop() >= $('.in-page-nav ol').closest('section').offset().top && $('.in-page-nav ol').css('bottom').replace("px", "") < $('aside').offset().top) {
			$('.in-page-nav ol').css('top',$(window).scrollTop() - $('.in-page-nav ol').closest('section').offset().top)
			$('.in-page-nav ol').css('bottom','')
		}
		else {
			$('.in-page-nav ol').css('top','')
			$('.in-page-nav ol').css('bottom','')
		}

		$('main section h2:not(nav h2)').each(function() {
			if($(window).scrollTop() >= $(this).offset().top - 1) {
				var subHeadId = $(this).attr("id")
				var subHeadNo = 'lnk'+ subHeadId
				$('.in-page-nav a').removeAttr('aria-current','page')
				$('.in-page-nav #' + subHeadNo).attr('aria-current','page')
			}
		})

		if($(window).scrollTop() < $('main section h2:first-of-type:not(nav h2)').offset().top) {
			$('.in-page-nav a').removeAttr('aria-current','page')
			$('.in-page-nav li:first-of-type a').attr('aria-current','page')
		}
	}

	function toggleMode(mode) {
		if(mode == 'system' || mode == '') {
			$('.mode button').removeClass('selected')
			$('#system').addClass('selected')
			const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
			if(userPrefersDark) {
				document.documentElement.setAttribute('colour-scheme', 'dark')
				localStorage.removeItem('colour-scheme')
			}
			else {
				document.documentElement.setAttribute('colour-scheme', 'light')
				localStorage.removeItem('colour-scheme')
			}
			window.matchMedia('(prefers-color-scheme: dark)').addListener(({ matches }) =>
			{
				if((mode == 'system' || mode == '') && matches) {
				document.documentElement.setAttribute('colour-scheme', 'dark')
				localStorage.removeItem('colour-scheme')
				} else if(mode == 'system' || mode == '') {
				document.documentElement.setAttribute('colour-scheme', 'light')
				localStorage.removeItem('colour-scheme')
				}
			})
		}
		else {
			document.documentElement.setAttribute('colour-scheme', mode)
			localStorage.setItem('colour-scheme', mode)
			$('.mode button').removeClass('selected')
			$('#' + mode).addClass('selected')
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
