// for test purposes
	// display 'less' errors
		less = {env: 'development'}

	$(document).ready(function() {
	// get parameters from querystring
		var getUrlParameter = function getUrlParameter(sParam) {
			var sPageURL = window.location.search.substring(1),
				sURLVariables = sPageURL.split('&'),
				sParameterName,
				i;

			for (i = 0; i < sURLVariables.length; i++) {
				sParameterName = sURLVariables[i].split('=');

				if (sParameterName[0] === sParam) {
					return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
				}
			}
			return false;
		}

	// if there is a timeline
		if($('section#timeline').length != 0) {

		// display from a range of examples
			var example = getUrlParameter('version')
			
			if(example == false || $('section[data-id="' + example + '"]').length == 0) {
				$('section#timeline').not('section[data-id="default"]').each(function() {
					$(this).remove()
				})
			}
			else {
				$('section#timeline').not('section[data-id="' + example + '"]').each(function() {
					$(this).remove()
				})
			}

		// set up metadata and status panels, specific to the example
			setTimeout(function() {
				if ($('section[data-id^="repealed"]').length != 0) {
					$('#legislation-metadata div:not(.repealed, .geographical-extent, .associated-documents, .other-formats, .other-formats div)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr h2:not(.repealed)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr p:not(.repealed)').remove()
				}
				else {
					$('.repealed').remove()
				}

				if ($('section[data-id^="prospective"]').length != 0 && $('li.current[aria-current="page"]').length == 0) {
					$('#legislation-metadata div:not(.prospective, .associated-documents, .other-formats, .other-formats div)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr h2:not(.prospective)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr p:not(.prospective)').remove()
				}
				else {
					$('.legislation-text li.prospective').removeClass('prospective')
					$('.legislation-text .prospective-message').remove()
					$('.prospective:not(.timeline, button, .versions, .versions li)').remove()
				}

				if ($('section[data-id^="concurrent"]').length != 0) {
					$('#legislation-metadata div:not(.up-to-date, .in-force, .concurrent, .associated-documents, .other-formats, .other-formats div)').remove()
				}
				else {
					$('.status-panel.extent[paneltype="commencement"] p.extent-info').remove()
					$('.status-panel.extent[paneltype="commencement"]').removeClass('extent')
					$('.concurrent').remove()
				}
				
				if ($('section[data-id^="not-up-to-date"]').length != 0) {
					$('#legislation-metadata div:not(.not-up-to-date, .associated-documents, .other-formats, .other-formats div)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr h2:not(.not-up-to-date)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr p:not(.not-up-to-date)').remove()
				}
				else {
					$('#notUpToDateStatus').remove()
					$('.not-up-to-date').remove()
				}

				if ($('section[data-id*="viewing-historical"]').length != 0 || $('section[data-id*="viewing-original"]').length != 0 || $('section[data-id*="historical-point-in-time"]').length != 0 || $('section[data-id*="viewing-original-point-in-time"]').length != 0) {
					$('#legislation-metadata div:not(.historical, .associated-documents, .other-formats, .other-formats div)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr h2:not(.historical)').remove()
					$('.status-panel[paneltype="commencement"] .status-hdr p:not(.historical)').remove()
				}
				else {
					$('.historical').remove()
				}
			},10)
		}

	// if there is legislation text
		if($('section#legislation-text').length != 0) {

		// display selected style of annotations
			var annotationsMethod = localStorage.getItem('annotation-style')
			if(annotationsMethod == null) {
				localStorage.setItem('annotation-style', 'default')
			}

			if(annotationsMethod == "hide") {
				$('section#legislation-text').not('section[data-id="default-annotations"]').each(function() {
					$(this).remove()
					$('ol.annotation').removeClass('annotation')
					$('.annotation-start').remove()
					$('.annotation-end').remove()
					$('.legislation-footnotes dt').remove()
					$('.legislation-footnotes dl').replaceWith(function(){
						return $("<ol>").append($(this).contents());
					});
					$('.legislation-footnotes dd').replaceWith(function(){
						return $("<li>").append($(this).contents());
					});
				})
			}
			else if($('section[data-id="' + annotationsMethod + '-annotations"]').length == 0) {
				$('section#legislation-text').not('section[data-id="default-annotations"]').each(function() {
					$(this).remove()
				})
			}
			else {
				$('section#legislation-text').not('section[data-id="' + annotationsMethod + '-annotations"]').each(function() {
					$(this).remove()
				})
			}

		// show/hide legislation text highlights
			var highlight = localStorage.getItem('annotation-highlight')
			if(highlight == null || highlight != "show") {
				$('span.annotation').contents().unwrap()
				$('ol.annotation').removeClass('annotation')
				$('span.not-up-to-date-highlight').contents().unwrap()
			}

			var notUpToDateHighlight = localStorage.getItem('notUpToDate-highlight')
			if(notUpToDateHighlight == null || notUpToDateHighlight != "show") {
				$('span.not-up-to-date.annotation-start').remove()
				$('span.not-up-to-date-highlight ~ span.annotation-end').remove()
				$('span.not-up-to-date-highlight').contents().unwrap()
				$('.legislation-footnotes .not-up-to-date dt a').contents().unwrap()
			}
		}
	})
// end test purposes
