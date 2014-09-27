# Adventure XBlock

Adventure XBlock is an XBlock for creating a simple
[chose your own adventure][wikipedia-cyoa] style simulation.

It presents the user with a branching sequence of steps,
each which can contain other `XBlockLightChildrens`.

Choosing a branch is mainly realized by selecting an option from
a [multiple choice question][mentoring-mcq].

It also has the ability to embed other `XBlockLightChildren`s such as
html, video, etc.

[wiki-cyoa]: https://en.wikipedia.org/wiki/Choose_Your_Own_Adventure
[mentoring-mcq]: https://github.com/edx-solutions/xblock-mentoring#self-assessment-mcqs

## Installation

Install the requirements into the python virtual environment of your
`edx-platform` installation by running the following command from the
root folder:

```bash
$ pip install -r requirements.txt
```

## Enabling in studio

You can enable the XBlock in studio through the advanced settings.

1. From the main page of a specific course, navigate to `Settings ->
   Advanced Settings` from the top menu.
2. Check for the `advanced_modules` policy key, and add `"adventure"`
   to the policy value list.
3. Click the "Save changes" button.


## Usage

When you add the `Adventure` component to a course in the studio, the
block is field with [default XML content][default-adventure].

The various xml elements are explained below.

### `<adventure>` element

The wrapping `<adventure>` element can contain the following child
elements:

* `<title>` - Renders the title of the block.
* `<info>` - Renders a shared info, it is displayed on every step, along with the title.
* `<step>` - A step of the adventure. A typical adventure has at least a couple of steps.

#### `<step>` element

A step element represent a simple step of the adventure.

The `<step>` element has the following attributes:

* `name`: The name of the step. It must be unique within an adventure, as this is how other steps refer to this one.
  The first step must be named `first`. This is how the adventure block finds the initial step for the adventure.
  This is a mandatory attribute.
* `back`: The name of the previous step, for backtracking. This is an optional attribute.
  If missing, the controls for getting back to the previous step is disabled.

* `next`: The name of the next step. This is an optional attribute.
  If missing and a choice mechanism such as `<mcq>` is present, it means this is a choice step.
  If missing and there are no such mechanism present, it means this is (one of the) final step(s) of the adventure.

The `<step>` element can contain various XBlockLightChild elements and other XBlocks, such as
`<html>`, `<title>`, `<mcq>`, `<ooyala-player>`. To know more about them, see [their][mentoring-doc] [documentation][ooyala-doc].

Of special interest is the `<mcq>` element, that can act as a selector for the next step.
In this case, the selected value of the choice must be a valid name for one of the steps.
Once selected, this choice will act the same way as if the step would have it as it's `next` attribute.

[mentoring-doc]: https://github.com/edx-solutions/xblock-mentoring
[ooyala-doc]: https://github.com/edx-solutions/xblock-ooyala

## Example

For a complete example, see the contents of the [default adventure][default-adventure]
a new adventure unit defaults to in the Studio.

[default-adventure]: adventure/templates/xml/adventure_default.xml

## Workbench installation, settings and testing

See [general instructions][workbench-instructions]
on installing, using and testing XBlocks with the workbench.

[workbench-instructions]: https://github.com/open-craft/xblock-sdk/blob/dragonfi-instructions-to-test-xblocks/README.md#testing-an-xblock
