import textcomps as tc
import pprint

rawtext = tc.Rawtext()
rawtext.add(tc.Text("testing 1"))
rawtext.add(tc.Selector("@a"))
rawtext.add(tc.Score("@a", "testing objective1"))
rawtext.add(tc.Score.a("testing objective2"))
rawtext.add(
    tc.Translate("%2", with_content = tc.Rawtext().add(
            tc.Selector("@s[...]"),
            tc.Text("condition true"),
            tc.Text("condition false")
        )
    )
)

pprint.pprint(rawtext)