# LittleOrange::Organizations::Organization

Resource schema for AWS Organizations Organization resource

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "LittleOrange::Organizations::Organization",
    "Properties" : {
        "<a href="#enabledpolicytypes" title="EnabledPolicyTypes">EnabledPolicyTypes</a>" : <i>[ <a href="enabledpolicytypes.md">EnabledPolicyTypes</a>, ... ]</i>,
        "<a href="#featureset" title="FeatureSet">FeatureSet</a>" : <i>String</i>
    }
}
</pre>

### YAML

<pre>
Type: LittleOrange::Organizations::Organization
Properties:
    <a href="#enabledpolicytypes" title="EnabledPolicyTypes">EnabledPolicyTypes</a>: <i>
      - <a href="enabledpolicytypes.md">EnabledPolicyTypes</a></i>
    <a href="#featureset" title="FeatureSet">FeatureSet</a>: <i>String</i>
</pre>

## Properties

#### EnabledPolicyTypes

The enabled policy types of the Organization root

_Required_: No

_Type_: List of <a href="enabledpolicytypes.md">EnabledPolicyTypes</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### FeatureSet

Specifies the feature set supported by the organization. Each feature set supports different levels of functionality.

_Required_: No

_Type_: String

_Allowed Values_: <code>ALL</code> | <code>CONSOLIDATED_BILLING</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the Id.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Arn

Returns the <code>Arn</code> value.

#### Id

Returns the <code>Id</code> value.

#### MasterAccountArn

Returns the <code>MasterAccountArn</code> value.

#### MasterAccountId

Returns the <code>MasterAccountId</code> value.

#### MasterAccountEmail

Returns the <code>MasterAccountEmail</code> value.

