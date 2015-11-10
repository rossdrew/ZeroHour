import html2text, markdown2

sampleHTML = """
 <HTML>
   <HEAD>
     <TITLE>Sample HTML</TITLE>
   </HEAD>

   <BODY>
     <B>Test Bold</B><BR/>
     <I>Test Italics</I><BR/>
     <UL>
       <LI>List Item 1</LI>
       <LI>List Item 2</LI>
       <LI>List Item 3</LI>
     </UL>
   </BODY>
 </HTML>"""

sampleRallyHTML = """
<u>Acceptance Criteria</u>
<div>
  <ul>
    <li>A tag is added on successful build in TC.</li>
    <li>TC only monitors the master branch.</li>
    <li>TC creates a new build for every commit.</li>
    <li>All release/dev branches are merged into master.</li>
  </ul>
</div>"""

anotherSampleRallyHTML = """
When a vin is entered that is not valid, the following exception can be seen in the error logs. This does not affect the customer but does affect logging.<br /><div>        <p class="p1"><span class="s1">[2015-05-27 11:54:34,070] DEBUG [catalina-exec-11] com.himex.restsupport.db.DBConnectionLookup - DB Connection closed by com.himex.inthub.controllers.commondata.services.CommonDataService.validateVIN(CommonDataService.java:269)</span></p> <p class="p1"><span class="s1">[2015-05-27 11:54:34,073] ERROR [catalina-exec-11] com.himex.inthub.controllers.commondata.objects.ResultsLogger - Error [{}]</span></p> <p class="p1"><span class="s1">java.lang.NullPointerException</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at com.himex.inthub.controllers.commondata.objects.ResultsLogger.log(ResultsLogger.java:29) [ResultsLogger.class:?]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at com.himex.inthub.controllers.commondata.services.CommonDataService.compatCheck(CommonDataService.java:227) [CommonDataService.class:?]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at com.himex.inthub.controllers.commondata.services.CommonDataService.check(CommonDataService.java:96) [CommonDataService.class:?]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at com.himex.inthub.soap.cd.CompatDBImpl.checkVIN(CompatDBImpl.java:76) [CompatDBImpl.class:?]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at com.himex.inthub.soap.cd.endpoint.CheckVINEndpoint.checkVINRequest(CheckVINEndpoint.java:32) [CheckVINEndpoint.class:?]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at sun.reflect.GeneratedMethodAccessor67.invoke(Unknown Source) ~[?:?]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43) ~[?:1.7.0_65]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at java.lang.reflect.Method.invoke(Method.java:606) ~[?:1.7.0_65]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at org.springframework.ws.server.endpoint.MethodEndpoint.invoke(MethodEndpoint.java:132) [spring-ws-2.1.0.RELEASE-all.jar:2.1.0.RELEASE]</span></p> <p class="p1"><span class="s1">&nbsp; &nbsp; &nbsp; &nbsp;at</span></p></div>
"""

print "\nOriginal HTML\n{}".format(anotherSampleRallyHTML)

toMarkdown = html2text.html2text(anotherSampleRallyHTML)
print "\nHTML to Markdown\n{}".format(toMarkdown)

toHTML = markdown2.markdown(toMarkdown)
print "\nMarkdown to HTML\n{}".format(toHTML)

backToMarkdown = html2text.html2text(toHTML)
print "\nHTML back to Markdown\n{}".format(backToMarkdown)

"""
 So HTML to Markdown is easy but changing back needs some work

"""