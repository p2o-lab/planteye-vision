import time
from opcua import Client, ua


class BioReactor:
    def __init__(self):
        self.opcua_client = Client('opc.tcp://10.6.51.40:4840/')
        self.opcua_client.set_user('admin')
        self.opcua_client.set_password('wago')
        self.opcua_client.connect()
        time.sleep(1)
        self.start_pressure_release()
        self.calibrate_vessel()
        self.start_pressure_seal()
        self.start_aerate()

    def start_pressure_seal(self):
        print('-- Bioreactor: Start pressurize seal service --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_PressurizeSeal_1.SetSealPressure.StateOpOp').set_value(True)
        time.sleep(1)
        pressure = ua.Variant(2, ua.VariantType.Float)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_PressurizeSeal_1.SetSealPressure.VOp').set_value(pressure)
        time.sleep(1)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_PressurizeSeal_1.ServiceControl.StateOpOp').set_value(True)
        time.sleep(1)
        command = ua.Variant(4, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_PressurizeSeal_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(1)

    def start_pressure_release(self):
        print('-- Bioreactor: Start pressure release service --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Pressure_Release_1.ServiceControl.StateOpOp').set_value(True)
        time.sleep(1)
        command = ua.Variant(4, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Pressure_Release_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(1)

    def start_aerate(self):
        print('-- Bioreactor: Start aerate service --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Aerate_1.ServiceControl.StateOpOp').set_value(True)
        time.sleep(1)
        command = ua.Variant(4, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Aerate_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(1)

    def calibrate_vessel(self):
        print('-- Bioreactor: Calibrate weight cells --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Calibrate_1.SetPoint.StateOpOp').set_value(True)
        time.sleep(1)
        weight = ua.Variant(30, ua.VariantType.Float)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Calibrate_1.SetPoint.VOp').set_value(weight)
        time.sleep(1)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Calibrate_1.ServiceControl.StateOpOp').set_value(True)
        time.sleep(1)
        command = ua.Variant(4, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Calibrate_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(5)
        command = ua.Variant(2, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Calibrate_1.ServiceControl.CommandOp').set_value(command)

    def set_rpm(self, rpm):
        print(f'-- Bioreactor: Set rpm to {rpm} --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.SetpointRPM.StateOpOp').set_value(True)
        time.sleep(2)
        rpm = ua.Variant(rpm, ua.VariantType.Float)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.SetpointRPM.VOp').set_value(rpm)
        time.sleep(2)

    def set_service_offline(self):
        print('-- Bioreactor: Set service stir to offline mode --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.ServiceControl.StateOffOp').set_value(True)
        time.sleep(2)

    def set_service_operator(self):
        print('-- Bioreactor: Set service stir to operator mode --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.ServiceControl.StateOpOp').set_value(True)
        time.sleep(2)

    def start_service(self):
        print('-- Bioreactor: Start service stir --')
        command = ua.Variant(4, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(2)

    def complete_service(self):
        print('-- Bioreactor: Complete service stir --')
        command = ua.Variant(1024, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(2)

    def reset_service(self):
        print('-- Bioreactor: Reset service stir --')
        command = ua.Variant(2, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Stir_1.ServiceControl.CommandOp').set_value(command)
        time.sleep(2)


class GasControl:
    def __init__(self):
        self.opcua_client = Client('opc.tcp://10.6.51.130:4840/')
        self.opcua_client.set_user('admin')
        self.opcua_client.set_password('wago')
        self.opcua_client.connect()
        time.sleep(1)

    def set_flow_rate(self, flow_rate):
        print(f'-- Gas control: Set gas flow to {flow_rate} --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.Flow_SP.StateOpOp').set_value(True)
        time.sleep(2)
        flow_rate = ua.Variant(flow_rate, ua.VariantType.Float)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.Flow_SP.VOp').set_value(flow_rate)
        time.sleep(2)

    def set_service_offline(self):
        print('-- Gas control: Set service to offline mode --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.ServiceControl.StateOffOp').set_value(True)
        time.sleep(2)

    def set_service_operator(self):
        print('-- Gas control: Set service to operator mode --')
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.ServiceControl.StateOpOp').set_value(True)
        time.sleep(2)

    def start_service(self):
        print('-- Gas control: Start service --')
        command = ua.Variant(4, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.ServiceControl.CommandOp').set_value(command)
        time.sleep(2)

    def complete_service(self):
        print('-- Gas control: Complete service --')
        command = ua.Variant(1024, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.ServiceControl.CommandOp').set_value(command)
        time.sleep(2)

    def reset_service(self):
        print('-- Gas control: Reset service --')
        command = ua.Variant(2, ua.VariantType.UInt32)
        self.opcua_client.get_node('ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.Service_Transfer_Media.ServiceControl.CommandOp').set_value(command)
        time.sleep(2)


print(f'====Initialisation====')
gc = GasControl()
br = BioReactor()
experiments = [{'gas_flow': 10.0, 'rpm': 100},
               {'gas_flow': 20.0, 'rpm': 150},
               {'gas_flow': 30.0, 'rpm': 250},
               ]

for exp in experiments:
    print(f'====Experiment {exp}====')

    # Stirring control
    br.set_service_offline()
    rpm = exp['rpm']
    br.set_rpm(rpm)
    br.set_service_operator()
    br.start_service()

    # Gas control
    gc.set_service_offline()
    gas_flow = exp['gas_flow']
    gc.set_flow_rate(gas_flow)
    gc.set_service_operator()
    gc.start_service()

    # Execution
    time.sleep(5)

    # Complete services and set to offline
    gc.complete_service()
    gc.reset_service()
    gc.set_service_offline()

    br.complete_service()
    br.reset_service()
    br.set_service_offline()

