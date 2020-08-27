# LilOrange::Organizations::Organization

Resource schema for AWS Organizations Organization resource

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "LilOrange::Organizations::Organization",
    "Properties" : {
        "<a href="#featureset" title="FeatureSet">FeatureSet</a>" : <i>String</i>,
    }
}
</pre>

### YAML

<pre>
Type: LilOrange::Organizations::Organization
Properties:
    <a href="#featureset" title="FeatureSet">FeatureSet</a>: <i>String</i>
</pre>

## Properties

#### FeatureSet

Specifies the feature set supported by the organization. Each feature set supports different levels of functionality.

_Required_: No

_Type_: String

_Allowed Values_: <code>ALL</code> | <code>CONSOLIDATED_BILLING</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the Id.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Arn

Returns the <code>Arn</code> value.

#### AvailablePolicyTypes

The policy types and associated status for this Organization

#### Id

Returns the <code>Id</code> value.

#### MasterAccountArn

Returns the <code>MasterAccountArn</code> value.

#### MasterAccountId

Returns the <code>MasterAccountId</code> value.

#### MasterAccountEmail

Returns the <code>MasterAccountEmail</code> value.

